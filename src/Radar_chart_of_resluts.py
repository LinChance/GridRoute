import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from math import pi
import os

# Create directory for radar charts if it doesn't exist
os.makedirs('./results/radar_chart', exist_ok=True)

# Load data
data = pd.read_csv('./results/overall.csv')
print("Data loaded with shape:", data.shape)
print("Columns:", data.columns.tolist())

# 检查数据中的关键列
if 'Size' not in data.columns:
    # 尝试查找可能的替代列名
    possible_size_columns = [col for col in data.columns if 'size' in col.lower() or 'matrix' in col.lower()]
    if possible_size_columns:
        print(f"'Size' column not found, using '{possible_size_columns[0]}' instead")
        data.rename(columns={possible_size_columns[0]: 'Size'}, inplace=True)
    else:
        raise ValueError("No 'Size' column found in the data")

if 'Prompt' not in data.columns:
    # 尝试查找可能的替代列名
    possible_prompt_columns = [col for col in data.columns if 'prompt' in col.lower() or 'template' in col.lower()]
    if possible_prompt_columns:
        print(f"'Prompt' column not found, using '{possible_prompt_columns[0]}' instead")
        data.rename(columns={possible_prompt_columns[0]: 'Prompt'}, inplace=True)
    else:
        raise ValueError("No 'Prompt' column found in the data")

# 打印唯一值以便调试
print("Unique Size values:", data['Size'].unique())
print("Unique Prompt values:", data['Prompt'].unique())

# 确保Size列的值是字符串类型
data['Size'] = data['Size'].astype(str)

# Define the metrics (in clockwise order)
categories = ['CR', 'FR', 'OR', 
              'GM', 'MSE', "Average Time"]

# 检查这些列是否存在
missing_categories = [cat for cat in categories if cat not in data.columns]
if missing_categories:
    print(f"Warning: The following categories are missing: {missing_categories}")
    # 尝试查找替代列
    for cat in missing_categories:
        possible_columns = [col for col in data.columns if cat.lower() in col.lower()]
        if possible_columns:
            print(f"Using '{possible_columns[0]}' for '{cat}'")
            categories[categories.index(cat)] = possible_columns[0]

N = len(categories)

# Get all unique Prompts
prompts = data['Prompt'].unique()
print(f"Found {len(prompts)} unique prompts: {prompts}")

# Get all unique Sizes from the data
all_sizes = [size for size in data['Size'].unique() if size.lower() != 'overall']
print(f"Found {len(all_sizes)} unique sizes (excluding 'Overall'): {all_sizes}")

# Sort sizes if they are numeric
try:
    numeric_sizes = []
    for size in all_sizes:
        try:
            numeric_sizes.append(int(size))
        except ValueError:
            # 如果无法转换为整数，保持原样
            numeric_sizes.append(size)
    all_sizes = sorted([str(size) for size in numeric_sizes])
except Exception as e:
    print(f"Error sorting sizes: {e}")
    all_sizes = sorted(all_sizes)  # Sort alphabetically if not numeric

# Add 'Overall' at the end if it exists
if 'Overall' in data['Size'].values or 'overall' in data['Size'].values:
    all_sizes.append('Overall')

print(f"Processing sizes: {all_sizes}")

# Create a radar chart for each Prompt and Size combination
for prompt in prompts:
    # Filter data for the current Prompt
    prompt_data = data[data['Prompt'] == prompt]
    
    # Skip if no data
    if len(prompt_data) == 0:
        print(f"No data for prompt: {prompt}")
        continue
    
    print(f"Processing prompt: {prompt}, found {len(prompt_data)} rows")
    
    # Get all unique models for this prompt to create a single legend later
    if 'Model' not in prompt_data.columns:
        # 尝试查找可能的替代列名
        possible_model_columns = [col for col in prompt_data.columns if 'model' in col.lower()]
        if possible_model_columns:
            print(f"'Model' column not found, using '{possible_model_columns[0]}' instead")
            prompt_data.rename(columns={possible_model_columns[0]: 'Model'}, inplace=True)
        else:
            print("No 'Model' column found, using a default value")
            prompt_data['Model'] = 'Unknown Model'
    
    all_models = prompt_data['Model'].unique()
    print(f"Found {len(all_models)} unique models: {all_models}")
    all_handles = []
    all_labels = []
    
    # Create radar charts for each Size
    for size in all_sizes:
        # Filter data for the current Size (case insensitive)
        size_data = prompt_data[prompt_data['Size'].str.lower() == size.lower()]
        
        # Skip if no data for this Size
        if len(size_data) == 0:
            print(f"  No data for size: {size}")
            continue
        
        print(f"  Processing size: {size}, found {len(size_data)} models")
        
        # Create figure for radar chart
        plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)
        
        # Calculate angles for each metric
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Process labels: if label has more than two words, add newline
        labels = [label.replace(' ', '\n') if len(label.split()) > 2 else label for label in categories]
        
        # Set radar chart parameters
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=20)
        # Adjust padding so that xtick labels are separated from the radar chart circles
        ax.tick_params(axis='x', pad=20)
        
        ax.set_rlabel_position(30)
        plt.yticks([0.25, 0.5, 0.75], ["0.25", "0.5", "0.75"], color="grey", size=10)
        plt.ylim(0, 1)
        
        # Add title for the radar chart
        plt.title(f"Prompt: {prompt}, Size: {size}", fontsize=16, pad=20)
        
        # Plot radar chart for each Model under the current Prompt and Size
        for _, row in size_data.iterrows():
            model_name = row['Model']
            print(f"    Processing model: {model_name}")
            
            # Extract and process data (handle NaN)
            values = []
            for col in categories:
                if col in row:
                    values.append(row[col] if not pd.isna(row[col]) else 0)
                else:
                    print(f"      Warning: Column '{col}' not found for model {model_name}")
                    values.append(0)
            
            # Normalize data based on global min and max for this size
            normalized = []
            for i, col in enumerate(categories):
                if col in data.columns:
                    # Get min and max values for this column across all models with the same size
                    size_specific_data = data[data['Size'].str.lower() == size.lower()]
                    if not size_specific_data.empty and col in size_specific_data.columns:
                        min_val = size_specific_data[col].min()
                        max_val = size_specific_data[col].max()
                        
                        # Normalize the value
                        if max_val - min_val != 0:
                            norm_val = (values[i] - min_val) / (max_val - min_val)
                        else:
                            norm_val = 0.5
                    else:
                        norm_val = 0.5
                else:
                    norm_val = 0.5
                normalized.append(norm_val)
            
            # Close the normalized data
            normalized += normalized[:1]
            
            # Plot radar chart line for the model
            line, = ax.plot(angles, normalized, linewidth=1.5, linestyle='solid', 
                    label=f"{model_name}", alpha=0.8)
            ax.fill(angles, normalized, alpha=0.05)
            
            # Store handle and label for the legend if this is the first time we see this model
            if model_name not in all_labels:
                all_handles.append(line)
                all_labels.append(model_name)
        
        # Save the radar chart as an image without legend
        output_path = f'./results/radar_chart/radar_chart_{prompt}_size_{size}.png'
        plt.savefig(output_path, dpi=1200, bbox_inches='tight')
        print(f"  Saved radar chart to: {output_path}")
        plt.close()  # Close the figure to free memory
    
    # Create a single legend figure for all models in this prompt
    if all_handles:
        # Create a new figure for the legend
        legend_fig = plt.figure(figsize=(10, 2))
        legend = legend_fig.legend(all_handles, all_labels, loc='center', ncol=len(all_handles),
                                  fontsize=12, title=f"Models for {prompt}", title_fontsize=14)
        legend_fig.tight_layout()
        legend_path = f'./results/radar_chart/legend_{prompt}.png'
        legend_fig.savefig(legend_path, dpi=1200, bbox_inches='tight')
        print(f"Saved legend to: {legend_path}")
        plt.close(legend_fig)  # Close the legend figure

print("All radar charts and legends have been generated successfully.")