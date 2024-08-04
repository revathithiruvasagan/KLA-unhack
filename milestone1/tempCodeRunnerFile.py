index or name
care_area_x_max = care_areas[2][0]  # Replace with actual index or name
care_area_y_min = care_areas[3][0]  # Replace with actual index or name
care_area_y_max = care_areas[4][0]  # Replace with actual index or name

# Define the main area size
main_area_size = 110

# Initialize an empty list to store main field coordinates
main_fields = []

# Adjust the initial x-coordinates for the first main field
main_field_x_start = care_area_x_min - 5  # expand slightly on the left
main_field_x_end = care_area_x_max + 5    # expand slightly on the right

# Create the main fields by expanding horizontally
for i in range(2):  # Assuming two main fields as per the output example
    main_field_x1 = main_field_x_start + i * main_a