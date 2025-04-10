import heapq
import ast
import pandas as pd

maps_df = pd.read_excel('./data/dataset.xlsx')


# Function to convert obstacles into a set of tuples for fast lookup
def get_obstacle_set(obstacles):
    # If obstacles are stored as a string, convert them to a list of tuples
    if isinstance(obstacles, str):
        obstacles = ast.literal_eval(obstacles)
    return set((x, y) for x, y in obstacles)


# Dijkstra's algorithm for path planning
def dijkstra_path(matrix_size, obstacle_set, start, end):
    # Initialize priority queue and visited set
    queue = [(0, start)]  # (cost, (x, y))
    visited = set()
    parent = {start: None}

    # Possible moves (no diagonal movement allowed)
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while queue:
        cost, current = heapq.heappop(queue)

        # If we reach the end point, reconstruct the path
        if current == end:
            path = []
            while current:
                path.append(current)
                current = parent[current]
            return path[::-1]  # Return the reversed path

        if current in visited:
            continue
        visited.add(current)

        # Explore neighbors
        for move in moves:
            neighbor = (current[0] + move[0], current[1] + move[1])

            # Check if the neighbor is within grid bounds, not in obstacles, and not visited
            if (0 <= neighbor[0] < matrix_size and 0 <= neighbor[1] < matrix_size and
                    neighbor not in obstacle_set and neighbor not in visited):

                if neighbor not in parent:  # Track the path
                    parent[neighbor] = current
                heapq.heappush(queue, (cost + 1, neighbor))

    # Return an empty path if no valid path exists
    return []


# Process each map for path planning
all_paths = []

for idx, row in maps_df.iterrows():
    matrix_size = row['matrix_size']
    obstacles = row['all_obstacle_coords']
    start_x, start_y = row['start_x'], row['start_y']
    end_x, end_y = row['end_x'], row['end_y']

    # Convert obstacles to a set
    obstacle_set = get_obstacle_set(obstacles)

    # Find path using Dijkstra's algorithm
    path = dijkstra_path(matrix_size, obstacle_set, (start_x, start_y), (end_x, end_y))

    # Format path as a string if found
    formatted_path = str(path) if path else "[]"

    # Append the result to the list
    all_paths.append({
        "Matrix_Size": matrix_size,
        "Start_X": start_x,
        "Start_Y": start_y,
        "End_X": end_x,
        "End_Y": end_y,
        "Path": formatted_path
    })

# Convert all paths to a DataFrame and save to Excel
all_paths_df = pd.DataFrame(all_paths)
all_paths_df.to_excel("./data/reference_paths.xlsx", index=False)
print("All planned paths have been saved to 'reference_paths.xlsx'.")
