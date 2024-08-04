import pandas as pd
from rtree import index

# Load data
care_areas = pd.read_csv(
    r"C:\Users\Revathi\Documents\GitHub\KLA-unhack\milestone2\dataset\CareAreas.csv",
    header=None,
    names=["ID", "X1", "X2", "Y1", "Y2"],
)
metadata = pd.read_csv(
    r"C:\Users\Revathi\Documents\GitHub\KLA-unhack\milestone2\dataset\metadata.csv",
    header=0,
)

print(metadata)

try:
    main_field_size = float(metadata.iloc[0, 0])
    sub_field_size = float(metadata.iloc[0, 1])
except ValueError as e:
    print("Error converting metadata to float:", e)
    raise

def check_overlap(x1, x2, y1, y2, fields):
    """Check if the field defined by (x1, x2, y1, y2) overlaps with any existing fields."""
    for _, field in fields.iterrows():
        if not (x2 <= field["X1"] or x1 >= field["X2"] or y2 <= field["Y1"] or y1 >= field["Y2"]):
            return True
    return False

def place_main_fields(care_areas, main_field_size):
    main_fields = []
    count = 0
    for _, row in care_areas.iterrows():
        x1, x2, y1, y2 = row["X1"], row["X2"], row["Y1"], row["Y2"]

        x_steps = int((x2 - x1) // main_field_size) + 1
        y_steps = int((y2 - y1) // main_field_size) + 1

        for y in range(y_steps):
            for x in range(x_steps):
                mf_x1 = x1 + x * main_field_size
                mf_y1 = y1 + y * main_field_size
                mf_x2 = mf_x1 + main_field_size
                mf_y2 = mf_y1 + main_field_size

                if (
                    mf_x2 <= x2
                    and mf_y2 <= y2
                    and not check_overlap(mf_x1, mf_x2, mf_y1, mf_y2, pd.DataFrame(main_fields, columns=["ID", "X1", "X2", "Y1", "Y2"]))
                ):
                    main_fields.append([count, mf_x1, mf_x2, mf_y1, mf_y2])
                    count += 1

    main_fields_df = pd.DataFrame(main_fields, columns=["ID", "X1", "X2", "Y1", "Y2"])
    return main_fields_df

main_fields = place_main_fields(care_areas, main_field_size)

# Uncomment this to save the main fields to a CSV file
# main_fields.to_csv(
#     r"C:\Users\Revathi\Documents\GitHub\KLA-unhack\milestone2\output\mainfields.csv",
#     index=False,
#     header=False,
# )

def place_sub_fields(main_fields, sub_field_size, care_areas):
    sub_fields = []
    sub_field_id = 0

    # Create R-tree index for care areas
    idx = index.Index()
    for _, care_row in care_areas.iterrows():
        idx.insert(care_row["ID"], (care_row["X1"], care_row["Y1"], care_row["X2"], care_row["Y2"]))

    for _, main_field in main_fields.iterrows():
        main_id = main_field["ID"]
        mf_x1, mf_x2, mf_y1, mf_y2 = (
            main_field["X1"],
            main_field["X2"],
            main_field["Y1"],
            main_field["Y2"],
        )

        x_steps = int((mf_x2 - mf_x1) // sub_field_size)
        y_steps = int((mf_y2 - mf_y1) // sub_field_size)

        for y in range(y_steps):
            for x in range(x_steps):
                sf_x1 = mf_x1 + x * sub_field_size
                sf_x2 = sf_x1 + sub_field_size
                sf_y1 = mf_y1 + y * sub_field_size
                sf_y2 = sf_y1 + sub_field_size

                # Ensure subfield is within the care areas
                candidates = list(idx.intersection((sf_x1, sf_y1, sf_x2, sf_y2)))
                within_care_area = any(
                    (care_row["X1"] <= sf_x1 <= care_row["X2"]
                     and care_row["X1"] <= sf_x2 <= care_row["X2"]
                     and care_row["Y1"] <= sf_y1 <= care_row["Y2"]
                     and care_row["Y1"] <= sf_y2 <= care_row["Y2"])
                    for _, care_row in care_areas[care_areas["ID"].isin(candidates)].iterrows()
                )

                if (
                    sf_x2 <= mf_x2
                    and sf_y2 <= mf_y2
                    and within_care_area
                    and not check_overlap(sf_x1, sf_x2, sf_y1, sf_y2, pd.DataFrame(sub_fields, columns=["Sub_Field_ID", "X1", "X2", "Y1", "Y2", "Main_ID"]))
                ):
                    sub_fields.append([sub_field_id, sf_x1, sf_x2, sf_y1, sf_y2, main_id])
                    sub_field_id += 1

    sub_fields_df = pd.DataFrame(
        sub_fields, columns=["Sub_Field_ID", "X1", "X2", "Y1", "Y2", "Main_ID"]
    )
    return sub_fields_df

def verify_coverage(care_areas, main_fields):
    covered_care_areas = []

    for care_index, care_row in care_areas.iterrows():
        covered = False
        for _, main_row in main_fields.iterrows():
            if (
                main_row["X1"] <= care_row["X1"]
                and main_row["X2"] >= care_row["X2"]
                and main_row["Y1"] <= care_row["Y1"]
                and main_row["Y2"] >= care_row["Y2"]
            ):
                covered = True
                break
        if covered:
            covered_care_areas.append(care_row["ID"])

    return covered_care_areas

covered_care_areas = verify_coverage(care_areas, main_fields)
print("Covered Care Areas:", covered_care_areas)

def optimize_main_fields(care_areas, main_fields, main_field_size):
    optimized_main_fields = main_fields.copy()
    for _, care_row in care_areas.iterrows():
        x1, x2, y1, y2 = care_row["X1"], care_row["X2"], care_row["Y1"], care_row["Y2"]

        covered = any(
            (main_row["X1"] <= x1 <= main_row["X2"] and main_row["Y1"] <= y1 <= main_row["Y2"])
            or (main_row["X1"] <= x2 <= main_row["X2"] and main_row["Y1"] <= y2 <= main_row["Y2"])
            for _, main_row in main_fields.iterrows()
        )

        if not covered:
            new_x1 = x1 - main_field_size / 2
            new_x2 = new_x1 + main_field_size
            new_y1 = y1 - main_field_size / 2
            new_y2 = new_y1 + main_field_size

            if not check_overlap(new_x1, new_x2, new_y1, new_y2, optimized_main_fields):
                new_main_field = pd.DataFrame(
                    [[len(optimized_main_fields), new_x1, new_x2, new_y1, new_y2]],
                    columns=["ID", "X1", "X2", "Y1", "Y2"],
                )
                optimized_main_fields = pd.concat(
                    [optimized_main_fields, new_main_field], ignore_index=True
                )

    return optimized_main_fields

optimized_main_fields = optimize_main_fields(care_areas, main_fields, main_field_size)

optimized_main_fields.to_csv(
    r"C:\Users\Revathi\Documents\GitHub\KLA-unhack\milestone2\output\mainfields1.csv",
    index=False,
    header=False,
)

covered_care_areas_after_optimization = verify_coverage(care_areas, optimized_main_fields)
print("Covered Care Areas After Optimization:", covered_care_areas_after_optimization)

subfields_df = place_sub_fields(optimized_main_fields, sub_field_size, care_areas)
subfields_df.to_csv(
    r"C:\Users\Revathi\Documents\GitHub\KLA-unhack\milestone2\output\subfields.csv",
    index=False,
    header=False,
)
