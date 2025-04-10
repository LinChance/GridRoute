import pandas as pd
import numpy as np
import ast
import os
import re

# Load data from the specified paths
api_planned_paths_path = './results/output_dir/deepseek_cot.xlsx'  # Updated file naming format
dijkstra_planned_map_paths_path = './data/reference.xlsx'
generated_maps_path = './data/dataset.xlsx'

# Extract model_name and template from file name
file_name = os.path.basename(api_planned_paths_path)
# Use regex to extract model_name and template
match = re.match(r'(.+)_(.+)\.xlsx', file_name)
if match:
    model_name = match.group(1)
    template = match.group(2)
else:
    # If no match, use default values
    model_name = file_name.split('.')[0]
    template = "unknown"

print(f"Processing file: {file_name}")
print(f"Extracted model_name: {model_name}, template: {template}")

api_paths_df = pd.read_excel(api_planned_paths_path, engine='openpyxl')
dijkstra_paths_df = pd.read_excel(dijkstra_planned_map_paths_path, engine='openpyxl')
generated_maps_df = pd.read_excel(generated_maps_path, engine='openpyxl')

# Rename columns
api_paths_df.rename(columns={"matrix_size": "Matrix_Size"}, inplace=True)
api_paths_df.rename(columns={"Run_Time": "run_time"}, inplace=True)
generated_maps_df.rename(columns={"matrix_size": "Matrix_Size"}, inplace=True)

# Clean path data
def clean_paths(paths_df):
    def safe_eval(path_str):
        try:
            path = ast.literal_eval(path_str)
            if isinstance(path, list) and all(isinstance(p, tuple) for p in path):
                return path
            else:
                return []
        except (ValueError, SyntaxError):
            return []

    paths_df['Path'] = paths_df['Path'].apply(safe_eval)
    return paths_df

api_paths_df = clean_paths(api_paths_df)
dijkstra_paths_df = clean_paths(dijkstra_paths_df)

# Validate path
def validate_path(path, start, end, obstacles, matrix_size):
    if not path:
        return False, 0, "Empty Path"
    if path[0] != start or path[-1] != end:
        return False, len(path), "Start/End Mismatch"
    for i in range(1, len(path)):
        prev_x, prev_y = path[i - 1]
        curr_x, curr_y = path[i]
        # Check if out of map bounds
        if curr_x < 0 or curr_x >= matrix_size or curr_y < 0 or curr_y >= matrix_size:
            return False, len(path), "Out of Bounds"
        if abs(curr_x - prev_x) + abs(curr_y - prev_y) != 1:
            return False, len(path), "Invalid Step Distance"
        if (curr_x, curr_y) in obstacles:
            return False, len(path), "Path Through Obstacle"
    return True, len(path), "Valid Path"

# Process paths
def process_paths(paths_df, generated_maps_df):
    results = []
    failure_reasons = {}
    for idx, row in paths_df.iterrows():
        try:
            path = row["Path"]
            start = (row["Start_X"], row["Start_Y"])
            end = (row["End_X"], row["End_Y"])
            matrix_size = row["Matrix_Size"]  # Get map size
            match = generated_maps_df[
                (generated_maps_df["start_x"] == start[0]) &
                (generated_maps_df["start_y"] == start[1]) &
                (generated_maps_df["end_x"] == end[0]) &
                (generated_maps_df["end_y"] == end[1]) &
                (generated_maps_df["Matrix_Size"] == matrix_size)
            ]
            if not match.empty:
                obstacles = ast.literal_eval(match.iloc[0]["all_obstacle_coords"])
                is_valid, path_length, failure_reason = validate_path(path, start, end, obstacles, matrix_size)
                if not is_valid:
                    if matrix_size not in failure_reasons:
                        failure_reasons[matrix_size] = {
                            "Empty Path": 0,
                            "Start/End Mismatch": 0,
                            "Invalid Step Distance": 0,
                            "Path Through Obstacle": 0,
                            "Out of Bounds": 0
                        }
                    failure_reasons[matrix_size][failure_reason] += 1
                results.append({
                    "Path_Index": idx,
                    "Matrix_Size": matrix_size,
                    "Valid": is_valid,
                    "Path_Length": path_length,
                    "Failure_Reason": failure_reason
                })
            else:
                results.append({
                    "Path_Index": idx,
                    "Matrix_Size": matrix_size,
                    "Valid": False,
                    "Path_Length": len(path),
                    "Failure_Reason": "No Matching Obstacles"
                })
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            results.append({
                "Path_Index": idx,
                "Matrix_Size": row.get("Matrix_Size", "Unknown"),
                "Valid": False,
                "Path_Length": 0,
                "Failure_Reason": "Processing Error"
            })
    return pd.DataFrame(results), failure_reasons

# Process and validate
api_results, api_failure_reasons = process_paths(api_paths_df, generated_maps_df)
dijkstra_results, dijkstra_failure_reasons = process_paths(dijkstra_paths_df, generated_maps_df)

# Calculate overall metrics
success_ratio = api_results['Valid'].mean()
api_results['Dijkstra_Path_Length'] = dijkstra_results.set_index('Path_Index')['Path_Length']
api_results['Generated_Successfully'] = api_results['Path_Length'] > 0

def compute_relative_path_length(row):
    if row['Valid'] and row['Dijkstra_Path_Length'] > 0:
        return row['Path_Length'] / row['Dijkstra_Path_Length']
    return np.nan

api_results['Relative_Path_Length'] = api_results.apply(compute_relative_path_length, axis=1)
relative_path_length_mean = np.exp(np.log(api_results['Relative_Path_Length'].dropna()).mean())

# Calculate the proportion of optimal paths
optimal_paths = api_results[
    (api_results['Valid'] == True) &  # Ensure path is valid
    (api_results['Path_Index'].isin(dijkstra_results[dijkstra_results['Valid'] == True]['Path_Index'])) &  # Ensure Dijkstra path is valid
    (api_results['Path_Length'] == api_results['Dijkstra_Path_Length'])  # Ensure path length matches Dijkstra path length
].shape[0]

# Calculate the proportion of optimal paths
optimal_ratio = optimal_paths / api_results['Valid'].sum() if api_results['Valid'].sum() > 0 else 0

average_success_time = api_paths_df[api_results['Generated_Successfully']]['run_time'].mean()
generated_success_ratio = api_results['Generated_Successfully'].mean()

# Calculate Mean Squared Error (MSE)
valid_paths = api_results[
    (api_results['Valid'] == True) &
    (dijkstra_results['Valid'] == True)
]
if not valid_paths.empty:
    mse = ((valid_paths['Path_Length'] - valid_paths['Dijkstra_Path_Length']) ** 2).mean()
else:
    mse = np.nan

# Calculate total number of successful paths
success_path_count = api_results['Valid'].sum()
print(f"Total number of successful paths: {success_path_count}")

# Calculate total number of optimal paths
optimal_path_count = api_results[
    (api_results['Valid'] == True) &  # Ensure path is valid
    (api_results['Path_Index'].isin(dijkstra_results[dijkstra_results['Valid'] == True]['Path_Index'])) &  # Ensure Dijkstra path is valid
    (api_results['Path_Length'] == api_results['Dijkstra_Path_Length'])  # Ensure path length matches Dijkstra path length
].shape[0]
print(f"Total number of optimal paths: {optimal_path_count}")

# Output path indices where path length is less than Dijkstra path length
shorter_paths = api_results[
    (api_results['Valid'] == True) &  # Ensure path is valid
    (api_results['Path_Length'] < api_results['Dijkstra_Path_Length'])  # Path length less than Dijkstra path length
]
print(f"Path indices with length less than Dijkstra path length: {shorter_paths['Path_Index'].tolist()}")
print("***************************************************************")
# Output path indices where path length is less than Dijkstra path length and is judged as correct
shorter_valid_paths = api_results[
    (api_results['Valid'] == True) &  # Ensure path is valid
    (api_results['Path_Length'] < api_results['Dijkstra_Path_Length'])  # Path length less than Dijkstra path length
]
print(f"Path indices with length less than Dijkstra path length and judged as correct: {shorter_valid_paths['Path_Index'].tolist()}")
print("***************************************************************")
# Print overall results
print(f"Proportion of successfully generated paths: {generated_success_ratio:.2%}")
print(f"Proportion of successful paths: {success_ratio:.2%}")
print(f"Geometric mean of relative path length: {relative_path_length_mean:.4f}")
print(f"Proportion of optimal paths: {optimal_ratio:.2%}")
print(f"Average time for successful path generation: {average_success_time:.2f} seconds")

# Print failed path analysis
print("\nOverall failed path analysis:")
for matrix_size, reasons in api_failure_reasons.items():
    print(f"Map size {matrix_size}:")
    for reason, count in reasons.items():
        print(f"  {reason}: {count}")

# Analyze by map size
grouped_results = api_results.groupby("Matrix_Size")
overall_results = []
target_sizes = [10, 20, 30]

for matrix_size, group in grouped_results:
    success_ratio = group['Valid'].mean()
    group['Dijkstra_Path_Length'] = dijkstra_results.set_index('Path_Index').loc[group.index, 'Path_Length']
    group['Generated_Successfully'] = group['Path_Length'] > 0

    def compute_relative_path_length(row):
        if row['Valid'] and row['Dijkstra_Path_Length'] > 0:
            return row['Path_Length'] / row['Dijkstra_Path_Length']
        return np.nan

    group['Relative_Path_Length'] = group.apply(compute_relative_path_length, axis=1)
    relative_path_length_mean = np.exp(np.log(group['Relative_Path_Length'].dropna()).mean())
    average_success_time = api_paths_df.loc[group.index][group['Generated_Successfully']]['run_time'].mean()
    generated_success_ratio = group['Generated_Successfully'].mean()

    # Add in the map size grouping loop
    valid_group_paths = group[
        (group['Valid'] == True) &
        (dijkstra_results.loc[group.index]['Valid'] == True)
        ]
    group_mse = ((valid_group_paths['Path_Length'] - valid_group_paths['Dijkstra_Path_Length']) ** 2).mean()

    optimal_paths = group[
        (group['Valid'] == True) &
        (group['Path_Length'] == group['Dijkstra_Path_Length'])
    ].shape[0]
    optimal_ratio = optimal_paths / group.shape[0]
    # Calculate geometric mean of relative path length, excluding failed paths
    valid_paths = api_results[api_results['Valid'] == True]
    valid_paths['Relative_Path_Length'] = valid_paths.apply(compute_relative_path_length, axis=1)
    relative_path_length_mean_new = np.exp(np.log(valid_paths['Relative_Path_Length'].dropna()).mean())

    print(f"Map size {matrix_size}:")
    print(f"  Proportion of successfully generated paths: {generated_success_ratio:.2%}")
    print(f"  Proportion of successful paths: {success_ratio:.2%}")
    print(f"  Geometric mean of relative path length: {relative_path_length_mean:.4f}")
    print(f"  Geometric mean of relative path length excluding failed paths: {relative_path_length_mean_new:.4f}")
    print(f"  Proportion of optimal paths: {optimal_ratio:.2%}")
    print(f"  Average time for successful path generation: {average_success_time:.2f} seconds")
    print(f"  Path length MSE: {group_mse:.4f}")

    # Store results for this matrix size
    result_entry = {
        "Size": str(matrix_size),  # Convert to string to ensure consistent type
        "CR": generated_success_ratio,
        "FR": success_ratio,
        "OR": optimal_ratio,
        "GM": relative_path_length_mean,
        "MSE": group_mse,
        "Average Time": average_success_time,
        "Model": model_name,
        "Prompt": template,
        "Source_File": file_name
    }
    
    overall_results.append(result_entry)

# Calculate overall MSE
if not valid_paths.empty:
    overall_mse = ((valid_paths['Path_Length'] - valid_paths['Dijkstra_Path_Length']) ** 2).mean()
else:
    overall_mse = np.nan

# Add overall results
overall_summary = {
    "Size": "Overall",  # Explicitly set Size to "Overall"
    "CR": generated_success_ratio,
    "FR": success_ratio,
    "OR": optimal_ratio,
    "GM": relative_path_length_mean,
    "MSE": overall_mse,
    "Average Time": average_success_time,
    "Model": model_name,
    "Prompt": template,
    "Source_File": file_name
}

# Add overall results to the list
overall_results.append(overall_summary)

# Convert to DataFrame
results_df = pd.DataFrame(overall_results)

# Add overall results description
print("\nOverall statistical results:")
print(f"Total test cases: {len(api_results)}")
print(f"Successfully generated paths: {success_path_count}")
print(f"Overall success rate: {generated_success_ratio:.2%}")
print(f"Overall feasibility rate: {success_ratio:.2%}")
print(f"Proportion of optimal paths: {optimal_ratio:.2%}")
print(f"Average relative path length: {relative_path_length_mean:.4f}")
print(f"Path length MSE: {overall_mse:.4f}")
print(f"Average generation time: {average_success_time:.2f} seconds")

# Ensure the results directory exists
os.makedirs('./data', exist_ok=True)
os.makedirs('./results', exist_ok=True)

# Save results to Excel file
output_file = './results/overall.xlsx'

# Check if file exists and append to it
try:
    existing_df = pd.read_excel(output_file, engine='openpyxl')
    
    # Remove any existing entries with the same Model and Prompt to avoid duplicates
    existing_df = existing_df[~((existing_df['Model'] == model_name) & 
                                (existing_df['Prompt'] == template))]
    
    # Append new results
    combined_df = pd.concat([existing_df, results_df], ignore_index=True)
except FileNotFoundError:
    combined_df = results_df

# Save to Excel
with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:
    combined_df.to_excel(writer, sheet_name='Results', index=False)

print(f"All results have been saved to {output_file}")