def choose_move(observation):
    # Defensive access to observation fields
    food_positions = observation.get('food', [])
    footprint = observation.get('footprint', [])
    opponents = observation.get('opponents', [])
    team = observation.get('team', [])
    my_position = observation.get('position', None)

    # Default move: no movement
    dx, dy = 0, 0

    # If position unknown, stay still
    if my_position is None:
        return [0, 0]
    x, y = my_position

    # Prioritize resource collection: move towards nearest food
    min_dist = float('inf')
    target = None
    for food in food_positions:
        fx, fy = food
        dist = abs(fx - x) + abs(fy - y)
        if dist < min_dist:
            min_dist = dist
            target = (fx, fy)

    if target:
        delta_x = target[0] - x
        delta_y = target[1] - y
        # Normalize to -1, 0, 1
        dx = (delta_x > 0) - (delta_x < 0)
        dy = (delta_y > 0) - (delta_y < 0)
        return [dx, dy]

    # No resource to pursue, attempt to explore or avoid opponents
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    for delta_x, delta_y in directions:
        nx, ny = x + delta_x, y + delta_y
        # Defensive check for footprint occupation
        if footprint:
            occupied = False
            for cell in footprint:
                if cell == (nx, ny):
                    occupied = True
                    break
            if occupied:
                continue
        # Check opponents for safety
        safe = True
        for opp in opponents:
            ox, oy = opp.get('position', (None, None))
            if ox is None or oy is None:
                continue
            if abs(ox - nx) + abs(oy - ny) <= 1:
                safe = False
                break
        if safe:
            return [delta_x, delta_y]

    # If all adjacent cells are unsafe, stay still
    return [0, 0]
