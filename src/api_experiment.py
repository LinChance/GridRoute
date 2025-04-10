import pandas as pd
import time
from openai import OpenAI
import re
import ast
import os
from prompt import Vanilla_prompt, independent_path_CoT, Few_shot_learning_prompt, algorithm_integration_CoT, Dijkstra_algorithm_prompt

# Initialize the OpenAI client
client = OpenAI(
    api_key='YOUR API KEY'
)

# Load the generated maps and start-end coordinates from the single DataFrame
maps_df = pd.read_csv("./data/dataset.csv", engine='openpyxl')

# Define the path planning function with retry mechanism
def planning(obstacles, start_x, start_y, end_x, end_y, map_info, template="independent", model_name="model_name"):
    # Choose the appropriate prompt template based on the provided 'template' parameter
    prompt_templates = {
        "vanilla": Vanilla_prompt,
        "independent": independent_path_CoT,
        "few_shot": Few_shot_learning_prompt,
        "algorithm": algorithm_integration_CoT,
        "dijkstra": Dijkstra_algorithm_prompt
    }
    chosen_template = prompt_templates.get(template, Vanilla_prompt)

    # Format the chosen template with the provided parameters
    prompt_text = chosen_template.format(
        prompt=obstacles,
        start_x=start_x,
        start_y=start_y,
        end_x=end_x,
        end_y=end_y
    )

    for attempt in range(3):  # Retry up to 3 times
        try:
            # Call the LLM API
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0.1
            )
            reply = response.choices[0].message.content.strip()

            # Validate the response
            if reply.startswith("[") and reply.endswith("]"):
                print(f"Path planning result - {map_info} (Attempt {attempt + 1}):\n{reply}\n")
                return reply
        except Exception as e:
            print(f"Error on attempt {attempt + 1} for {map_info}: {e}")

    # If all attempts fail, return an empty path
    print(f"Path planning failed for {map_info} after 3 attempts. Returning empty path.\n")
    return "[]"


# Process each map for path planning
def run_experiment(model_name="model_name", template="independent"):
    all_paths = []

    for idx, row in maps_df.iterrows():
        matrix_size = row['matrix_size']

        # Parse obstacles from string to Python data structure
        obstacles = ast.literal_eval(row['obstacles'])

        start_x, start_y = row['start_x'], row['start_y']
        end_x, end_y = row['end_x'], row['end_y']

        # Format obstacles into the required string format
        obstacle_coordinates = "[" + ", ".join(
            [f"(({obs['top_left'][0]}, {obs['top_left'][1]}), ({obs['bottom_right'][0]}, {obs['bottom_right'][1]}))" for obs in obstacles]
        ) + "]"

        print(obstacle_coordinates)

        # Record the start time
        start_time = time.time()

        # Call the path planning function
        map_info = f"Map {idx + 1} (Size: {matrix_size}x{matrix_size})"
        result = planning(obstacle_coordinates, start_x, start_y, end_x, end_y, map_info, template, model_name)

        # Record the end time and compute the runtime
        end_time = time.time()
        run_time = end_time - start_time
        print(f"{map_info} Runtime: {run_time:.2f} seconds\n")

        # Append the result to the list with map information
        all_paths.append({
            "Matrix_Size": matrix_size,
            "Start_X": start_x,
            "Start_Y": start_y,
            "End_X": end_x,
            "End_Y": end_y,
            "Obstacles": obstacle_coordinates,
            "Path": result,
            "Run_Time": run_time
        })

    # Clean up the paths by retaining only the valid bracketed content
    def keep_brackets_content(text):
        pattern = r'\[.*?\]'
        matches = re.findall(pattern, text)
        return ' '.join(matches)

    # Convert all paths to a DataFrame and clean up the Path column
    all_paths_df = pd.DataFrame(all_paths)
    all_paths_df['Path'] = all_paths_df['Path'].apply(keep_brackets_content)

    # Create output directory if it doesn't exist
    os.makedirs("./results/output_dir", exist_ok=True)

    # Save the planned paths to an Excel file with model name and template in the filename
    output_filename = f"./results/output_dir/{model_name}_{template}.csv"
    all_paths_df.to_csv(output_filename, index=False)
    print(f"All planned paths have been saved to '{output_filename}'.")
    
    return output_filename

# Run the experiment with specified model and template
if __name__ == "__main__":
    # You can change these parameters as needed
    model_name = "model_name"  # Replace with actual model name
    template = "independent"   # Choose from: vanilla, independent, few_shot, algorithm, dijkstra
    
    output_file = run_experiment(model_name, template)