import pandas as pd
import numpy as np




care_areas = pd.read_csv(r'C:\Users\Revathi\Downloads\Dataset-0\Dataset-0\1st\CareAreas.csv', header=None ,names=['ID', 'X1', 'X2', 'Y1', 'Y2'])

metadata = pd.read_csv(r'C:\Users\Revathi\Downloads\Dataset-0\Dataset-0\1st\metadata.csv', header=0)  

print(metadata)

try:
    main_field_size = float(metadata.iloc[0, 0])
    sub_field_size = float(metadata.iloc[0, 1])
except ValueError as e:
    print("Error converting metadata to float:", e)
    raise

def place_main_fields(care_areas, main_field_size):
    main_fields = []
    count = 0
    for _, row in care_areas.iterrows():
        x1, x2, y1, y2 = row['X1'], row['X2'], row['Y1'], row['Y2']
        mf_x1 = x1
        mf_y1 = y1
        mf_x2 = mf_x1 + main_field_size
        mf_y2 = mf_y1 + main_field_size

        main_fields.append([count, mf_x1-5, mf_x2-5, mf_y1-5, mf_y2-5])
        count += 1
    main_fields_df = pd.DataFrame(main_fields, columns=['ID', 'X1', 'X2', 'Y1', 'Y2'])
   
    return main_fields_df


main_fields = place_main_fields(care_areas, main_field_size)

main_fields.to_csv(r'C:\Users\Revathi\Documents\GitHub\KLA-unhack\milestone1\output\mainfields.csv', index=False, header=False)

def place_sub_fields(main_fields, sub_field_size):
    sub_fields = []
    sub_field_id = 0

    for index, main_field in main_fields.iterrows():
        main_id = main_field['ID']
        mf_x1, mf_x2, mf_y1, mf_y2 = main_field['X1'], main_field['X2'], main_field['Y1'], main_field['Y2']

        x_steps = int((mf_x2 - mf_x1) // sub_field_size)
        y_steps = int((mf_y2 - mf_y1) // sub_field_size)

        for y in range(y_steps):
            for x in range(x_steps):
                sf_x1 = mf_x1 + x * sub_field_size
                sf_x2 = sf_x1 + sub_field_size
                sf_y1 = mf_y1 + y * sub_field_size
                sf_y2 = sf_y1 + sub_field_size

                if sf_x2 <= mf_x2 and sf_y2 <= mf_y2:
                    sub_fields.append([sub_field_id, sf_x1, sf_x2, sf_y1, sf_y2, main_id])
                    sub_field_id += 1

    sub_fields_df = pd.DataFrame(sub_fields, columns=['Sub_Field_ID', 'X1', 'X2', 'Y1', 'Y2', 'Main_ID'])
    return sub_fields_df

sub_fields = place_sub_fields(main_fields, sub_field_size)

sub_fields.to_csv(r'C:\Users\Revathi\Documents\GitHub\KLA-unhack\milestone1\output\subfields.csv', index=False, header=False)
