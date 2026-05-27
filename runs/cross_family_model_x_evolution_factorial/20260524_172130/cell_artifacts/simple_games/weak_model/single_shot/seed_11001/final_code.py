def choose_move(observation):
    # Defensive access to observation fields with .get, defaulting to empty or neutral values
    grid = observation.get('grid', [])
    agents = observation.get('agents', [])
    resources = observation.get('resources', [])
    teammates = observation.get('teammates', [])
    opponents = observation.get('opponents', [])
    my_pos = observation.get('position', None)
    role = observation.get('role', None)
    
    if my_pos is None:
        return [0, 0]
    
    x, y = my_pos

    # Function to check if a position is within grid bounds
    def in_bounds(px, py):
        return 0 <= px < len(grid) and 0 <= py < len(grid[0]) if grid else False

    # Gather nearby items
    nearby_resources = []
    nearby_opponents = []
    for res in resources:
        rx, ry = res.get('position', (None, None))
        if rx is None or ry is None:
            continue
        dist = abs(rx - x) + abs(ry - y)
        if dist == 1:
            nearby_resources.append((rx, ry))
    for opp in opponents:
        ox, oy = opp.get('position', (None, None))
        if ox is None or oy is None:
            continue
        dist = abs(ox - x) + abs(oy - y)
        if dist == 1:
            nearby_opponents.append((ox, oy))
    
    # Prioritize resource collection if resources are nearby
    if nearby_resources:
        target = nearby_resources[0]
        dx = target[0] - x
        dy = target[1] - y
        if abs(dx) > abs(dy):
            return [1 if dx > 0 else -1, 0]
        elif dy != 0:
            return [0, 1 if dy > 0 else -1]
        else:
            return [0, 0]
    
    # Pursue opponents if any are nearby
    if nearby_opponents:
        target = nearby_opponents[0]
        dx = target[0] - x
        dy = target[1] - y
        if abs(dx) > abs(dy):
            return [1 if dx > 0 else -1, 0]
        elif dy != 0:
            return [0, 1 if dy > 0 else -1]
        else:
            return [0, 0]
    
    # For territory control or movement towards known owned areas or center
    # Try to move towards the center of the grid
    center_x = len(grid) // 2 if grid else x
    center_y = len(grid[0]) // 2 if grid and len(grid[0]) else y
    dx = center_x - x
    dy = center_y - y
    if abs(dx) > abs(dy):
        return [1 if dx > 0 else -1, 0]
    elif dy != 0:
        return [0, 1 if dy > 0 else -1]
    else:
        # No specific target, stand still
        return [0, 0]
