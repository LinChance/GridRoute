import pandas as pd
import random
import math
from scipy.spatial import ConvexHull

# Seed for reproducibility
random.seed(42)

# Function to calculate Euclidean distance
def euclidean_distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


# Function to check if points are within convex hull
def is_obstacle_in_path(start, end, obstacles):
    points = [start, end] + obstacles
    if len(points) < 3:
        return False
    hull = ConvexHull(points)
    hull_points = [tuple(points[v]) for v in hull.vertices]
    return any(point in hull_points for point in obstacles)


# Function to generate square obstacles without overlap
def generate_square_obstacles(matrix_size, obstacle_size, num_obstacles):
    obstacles = []
    all_obstacle_points = set()

    attempts = 0
    while len(obstacles) < num_obstacles and attempts < 1000:
        top_left_x = random.randint(0, matrix_size - obstacle_size)
        top_left_y = random.randint(0, matrix_size - obstacle_size)

        new_obstacle_points = set((i, j) for i in range(top_left_x, top_left_x + obstacle_size)
                                  for j in range(top_left_y, top_left_y + obstacle_size))

        if all_obstacle_points.isdisjoint(new_obstacle_points):
            obstacles.append({"top_left": (top_left_x, top_left_y),
                              "bottom_right": (top_left_x + obstacle_size - 1, top_left_y + obstacle_size - 1)})
            all_obstacle_points.update(new_obstacle_points)
        attempts += 1

    return obstacles, all_obstacle_points


# Function to check if path exists (simplified BFS for edge case validation)
def is_path_available(matrix_size, start, end, obstacles_set):
    from collections import deque
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    queue = deque([start])
    visited = set()

    while queue:
        x, y = queue.popleft()
        if (x, y) == end:
            return True
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < matrix_size and 0 <= ny < matrix_size and (nx, ny) not in obstacles_set and (
            nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
    return False


# Function to generate maps with obstacles and start/end points
def generate_maps(matrix_size, obstacle_size, num_obstacles, num_maps, num_start_end_pairs):
    all_maps = []
    grid_diagonal = math.hypot(matrix_size - 1, matrix_size - 1)

    for _ in range(num_maps):
        obstacles, all_obstacle_points = generate_square_obstacles(matrix_size, obstacle_size, num_obstacles)
        obstacles_set = set(all_obstacle_points)

        start_end_pairs = []
        attempts = 0

        while len(start_end_pairs) < num_start_end_pairs and attempts < 1000:
            start = (random.randint(0, matrix_size - 1), random.randint(0, matrix_size - 1))
            end = (random.randint(0, matrix_size - 1), random.randint(0, matrix_size - 1))

            distance = euclidean_distance(start, end)

            if start != end and start not in obstacles_set and end not in obstacles_set and distance >= 0.3 * grid_diagonal:
                if is_obstacle_in_path(start, end, list(obstacles_set)):
                    if is_path_available(matrix_size, start, end, obstacles_set):
                        start_end_pairs.append({'start_x': start[0], 'start_y': start[1],
                                                'end_x': end[0], 'end_y': end[1]})
            attempts += 1

        all_maps.append({
            'matrix_size': matrix_size,
            'obstacles': obstacles,
            'all_obstacle_points': list(obstacles_set),
            'start_end_pairs': start_end_pairs
        })

    return all_maps

# Parameters for each map size
map_configs = [
    {"matrix_size": 10, "obstacle_size": 3, "num_obstacles": 2, "num_maps": 100, "num_start_end_pairs": 5},
    {"matrix_size": 20, "obstacle_size": 4, "num_obstacles": 3, "num_maps": 100, "num_start_end_pairs": 5},
    {"matrix_size": 30, "obstacle_size": 5, "num_obstacles": 4, "num_maps": 100, "num_start_end_pairs": 5}
]

# Generate maps for all configurations
all_generated_maps = []
for config in map_configs:
    generated_maps = generate_maps(**config)
    all_generated_maps.extend(generated_maps)

# Convert the generated data to a structured DataFrame
all_data = []
for map_data in all_generated_maps:
    matrix_size = map_data['matrix_size']
    for pair in map_data['start_end_pairs']:
        all_data.append({
            "matrix_size": matrix_size,
            "obstacles": [
                {
                    "top_left": obs['top_left'],
                    "bottom_right": obs['bottom_right']
                } for obs in map_data['obstacles']
            ],
            "all_obstacle_coords": map_data['all_obstacle_points'],
            **pair
        })

maps_df = pd.DataFrame(all_data)
maps_df.to_csv("./data/dataset.csv", index=False)
