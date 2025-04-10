import pandas as pd
import matplotlib.pyplot as plt
import ast
import os

# Load obstacle and path data from Excel files
maps_df = pd.read_csv(r'./data/dataset.csv', engine='openpyxl')  # Load maps data
api_paths_df = pd.read_csv(r'./results/output_dir/model_name_template.csv', engine='openpyxl')  # Load paths data


# Ensure the directory exists for saving the plots
output_dir = "./results/api_planned_paths_figure/modelname"
os.makedirs(output_dir, exist_ok=True)

# Process each map and associated path
for idx, row in api_paths_df.iterrows():
    matrix_size = row['Matrix_Size']
    start_x, start_y = row['Start_X'], row['Start_Y']
    end_x, end_y = row['End_X'], row['End_Y']

    # Extract obstacles for the corresponding map
    map_row = maps_df.iloc[idx]
    obstacles_str = map_row['all_obstacle_coords']
    obstacles = ast.literal_eval(obstacles_str) if isinstance(obstacles_str, str) else obstacles_str

    # Extract obstacle coordinates
    x_coords, y_coords = zip(*obstacles) if obstacles else ([], [])

    # Parse the path from the current row
    path_str = row['Path']
    path_points = ast.literal_eval(path_str)  # Convert path string to a list

    # Check if path_points is not empty
    if not path_points:
        continue

    x1_coords, y1_coords = zip(*path_points)  # Split x and y coordinates

    # Set up the plot for the current path
    plt.figure(figsize=(8, 8))
    plt.scatter(x_coords, y_coords, c='black', marker='s', label="Obstacles")
    plt.plot(x1_coords, y1_coords, c='red', marker='o', label="Path", linestyle='-')  # Plot path

    # Draw arrows between each consecutive point in the path
    for k in range(len(x1_coords) - 1):
        dx = x1_coords[k + 1] - x1_coords[k]  # Difference in x direction
        dy = y1_coords[k + 1] - y1_coords[k]  # Difference in y direction
        plt.quiver(x1_coords[k], y1_coords[k], dx, dy, angles='xy', scale_units='xy', scale=1, color='blue', alpha=0.7)

    # Set plot details
    plt.title(f"Path with Obstacles - Map {idx + 1}")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.xlim(-1, matrix_size)  # Adjust to fit the matrix size with padding
    plt.ylim(-1, matrix_size)
    plt.legend()

    # Save each path plot as a separate PDF
    plt.savefig(os.path.join(output_dir, f"Dijkstra_path_map_{idx + 1}.png"))
    plt.close()