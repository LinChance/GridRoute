# independent path planning prompt
Vanilla_prompt = (
    f"Given these obstacle coordinates in a grid:\n{prompt}\n\n"
    f"Please independently plan a continuous path of coordinates from the starting point ({start_x}, {start_y}) "
    f"to the ending point ({end_x}, {end_y}), avoiding all obstacles listed above. "
    "The path must follow these rules:\n"
    "1. Every point must differ by exactly 1 in either x or y direction from the previous point (no diagonal moves allowed).\n"
    "2. The output should be in the format: [(x1, y1), (x2, y2), (x3, y3), ...].\n"
    "3. If a valid path cannot be created without touching an obstacle, return an empty path [].\n"
    "Return only the path without any additional explanation."
)

independent_path_CoT = (
    f"Here are the obstacle coordinates in the grid:\n{prompt}\n\n"
    f"You need to plan a path from the starting point ({start_x}, {start_y}) to the ending point ({end_x}, {end_y}) while avoiding the obstacles. "
    f"To ensure accuracy, follow these steps step by step:\n\n"
    f"1. Verify that the starting point ({start_x}, {start_y}) and ending point ({end_x}, {end_y}) are not obstacles.\n"
    f"2. List all valid moves for a point in the grid. A move is valid if:\n"
    f"   - It differs by exactly 1 in either the x or y direction from the previous point.\n"
    f"   - It does not overlap with any obstacle.\n"
    f"3. Starting from ({start_x}, {start_y}), iteratively choose the next valid move to build a path to ({end_x}, {end_y}).\n"
    f"4. If there is no valid path, return an empty path [].\n\n"
    f"Return the final path in this format: [(x1, y1), (x2, y2), (x3, y3), ...]. If there are any errors or no valid paths, return [].\n"
    f"Make sure to provide only the path in your response without any extra explanations."
)

Few_shot_learning_prompt = (
    f"Plan the shortest path from the starting point ({start_x}, {start_y}) to the endpoint ({end_x}, {end_y}) while avoiding rectangular obstacles defined as {prompt}. Follow these steps:\n\n"
    f"1. Analyze the grid to identify the start, end, and rectangular obstacle locations.\n"
    f"2. Each rectangle is defined by its top-left corner (x1, y1) and bottom-right corner (x2, y2). A grid cell (x, y) is an obstacle if x1 ≤ x ≤ x2 and y1 ≤ y ≤ y2.\n\n"
    f"3. Define valid moves:\n"
    f" - Right: (x, y+1)\n"
    f" - Left: (x, y-1)\n"
    f" - Down: (x+1, y)\n"
    f" - Up: (x-1, y)\n"
    f" - All moves must stay within the grid bounds and avoid obstacle cells.\n\n"
    f"4. Build the path:\n"
    f" - Start at ({start_x}, {start_y}).\n"
    f" - At each step, evaluate valid moves and select the one that minimizes the distance to ({end_x}, {end_y}).\n\n"
    f"5. If no valid moves are available, return an empty path [].\n\n"
    f"6. Output the result in this format: [(x1, y1), (x2, y2), ..., (xn, yn)].\n\n"
    f"Example 1:\n"
    f"Start: (3, 7), End: (4, 3), Obstacles: [((1, 2), (3, 4)), ((2, 5), (4, 6))]\n"
    f"Path: [(3, 7), (4, 7), (5, 7), (5, 6), (5, 5), (5, 4), (5, 3), (4, 3)]\n\n"
    f"Example 2:\n"
    f"Start: (2, 4), End: (7, 5), Obstacles: [((3, 4), (5, 6))]\n"
    f"Path: [(2, 4), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (7, 4), (7, 5)]\n\n"
    f"Return only the path as output, without additional explanations."
)

# algorithm integration
algorithm_integration_CoT = (
    f"Plan the shortest path from the starting point ({start_x}, {start_y}) to the endpoint ({end_x}, {end_y}) while avoiding rectangular obstacles defined as {prompt}. Use Dijkstra's algorithm to calculate the shortest path. Follow these steps:\n\n"

    f"1. Analyze the grid to identify the start, end, and rectangular obstacle locations.\n"
    f"2. Each rectangle is defined by its top-left corner (x1, y1) and bottom-right corner (x2, y2). A grid cell (x, y) is an obstacle if x1 ≤ x ≤ x2 and y1 ≤ y ≤ y2.\n\n"

    f"3. Define valid moves:\n"
    f"   - Right: (x, y+1)\n"
    f"   - Left: (x, y-1)\n"
    f"   - Down: (x+1, y)\n"
    f"   - Up: (x-1, y)\n"
    f"   - All moves must stay within the grid bounds and avoid obstacle cells.\n\n"

    f"4. Use Dijkstra's algorithm:\n"
    f"   - Assign an initial distance of infinity to all grid cells except the starting point, which should have a distance of 0.\n"
    f"   - Use a priority queue to repeatedly select the grid cell with the smallest tentative distance.\n"
    f"   - For each selected cell, evaluate its valid neighbors and update their tentative distances if a shorter path is found.\n"
    f"   - Continue until the endpoint ({end_x}, {end_y}) is reached or all possible paths have been explored.\n\n"

    f"5. Construct the path:\n"
    f"   - Start at ({start_x}, {start_y}).\n"
    f"   - Trace back from the endpoint to the starting point using the recorded parent cells to reconstruct the shortest path.\n"
    f"   - If no valid moves are available, return an empty path [].\n\n"

    f"6. Output the result in this format: [(x1, y1), (x2, y2), ..., (xn, yn)].\n\n"

    f"Return only the path as output, without additional explanations."
)

Dijkstra_algorithm_prompt = (
    f"Here are the obstacle coordinates in the grid:\n{obstacles}\n\n"
    f"You need to plan a path from the starting point ({start_x}, {start_y}) to the ending point ({end_x}, {end_y}) while avoiding the obstacles. "
    f"Use Dijkstra's algorithm principles to ensure the path is valid and follows the shortest possible route. Follow these steps:\n\n"

    f"1. Verify the starting point ({start_x}, {start_y}) and ending point ({end_x}, {end_y}) are not obstacles.\n\n"

    f"2. Define the cost of reaching a point in the grid:\n"
    f"   - Start by assigning a cost of 0 to the starting point ({start_x}, {start_y}).\n"
    f"   - For all other points, initialize the cost as infinity (∞).\n\n"

    f"3. Use a priority queue to iteratively explore points in the grid:\n"
    f"   - Begin with the starting point ({start_x}, {start_y}) in the queue.\n"
    f"   - At each step, select the point with the lowest current cost.\n"
    f"   - For each valid move (up, down, left, right):\n"
    f"     a. If moving to a neighboring point reduces its cost, update the cost and add the point to the queue.\n"
    f"     b. A move is valid if it does not overlap with any obstacle and stays within the grid.\n\n"

    f"4. Repeat this process until reaching the ending point ({end_x}, {end_y}) or exhausting all valid points in the queue:\n"
    f"   - If the ending point is reached, reconstruct the path by tracing back from the endpoint to the start using the cost values.\n"
    f"   - If no valid path exists, return an empty path [].\n\n"

    f"5. Return the final path in this format: [(x1, y1), (x2, y2), (x3, y3), ...]. If there are any errors or no valid paths, return [].\n\n"

    f"Example:\n"
    f"Start: (3, 7), End: (4, 3), Obstacles: [((1, 2), (3, 4)), ((2, 5), (4, 6))], grid: 10 \n\n"

    f"Evaluate valid neighbors in given map:\n"
    f"- Starting at (3, 7), distance is 0 :\n"
    f"  - (3, 6): Obstructed, skip.\n"
    f"  - (4, 7): Valid, update distance to 1.\n"
    f"  - (2, 7): Valid, update distance to 1.\n"
    f"  - (3, 8): Valid, update distance to 1.\n\n"

    f"- To (3, 6): Obstructed point.\n"

    f"- To (3, 8), recorded distance is 1:\n"
    f"  - (3, 7): Start point, distance is 0.\n"
    f"  - (4, 8): Valid, update distance to 2.\n"
    f"  - (2, 8): Valid, update distance to 2.\n"
    f"  - (3, 9): Valid, update distance to 2.\n\n"

    f"- To (3, 9), recorded distance is 2:\n"
    f"  - (3, 8):  Already visited, distance is,3, but recorded distance is 1 < 3, so distance stays at 1.\n"
    f"  - (4, 9): Valid, update distance to 3.\n"
    f"  - (2, 9): Valid, update distance to 3.\n"
    f"  - (3, 10): Out of grids, skip.\n\n"

    f"- To (4, 9), recorded distance is 3:\n"
    f"  - (4, 8): Already visited, distance is 4, but recorded distance is 2 < 4, so distance stays at 2.\n"
    f"  - (5, 9): Valid, update distance to 4.\n"
    f"  - (3, 9): Already visited, distance is 4, but recorded distance is 2 < 4, so distance stays at 2.\n"
    f"  - (4, 10): Out of grids, skip.\n\n"

    f"- To (5, 9), recorded distance is 4:\n"
    f"  - (5, 8): Valid, update distance to 5.\n"
    f"  - (6, 9): Valid, update distance to 5.\n"
    f"  - (4, 9): Already visited, distance is 5, but recorded distance is 3 < 4, so distance stays at 3.\n"
    f"  - (5, 10): Out of grids, skip.\n\n"

    f"- To (4, 8), recorded distance is 2:\n"
    f"  - (4, 7): Already visited, distance is 3, but recorded distance is 1 < 3, so distance stays at 1.\n"
    f"  - (5, 8): Already visited, distance is 3, but recorded distance is 5 > 3, so distance updates to 3.\n"
    f"  - (3, 8): Already visited, distance is 3, but recorded distance is 1 < 3, so distance stays at 1.\n"
    f"  - (4, 9): Already visited, distance is 3 which is equal to recorded distance, so distance stays at 3.\n\n"

    f"  - Traverse all point in the map\n\n"

    f"- Result: the distance of (4,3) is 7, which means (3,7) to (4,3) need 7 steps.\n\n"

    f"- Generated Path: [(3, 7), (4, 7), (5, 7), (5, 6), (5, 5), (5, 4), (4, 4), (4, 3)]\n\n"

    f"Now, apply the same logic to plan a path from ({start_x}, {start_y}) to ({end_x}, {end_y}) while avoiding the obstacles:\n"
    f"Make sure to provide only the path in your response without any extra explanations."
)
