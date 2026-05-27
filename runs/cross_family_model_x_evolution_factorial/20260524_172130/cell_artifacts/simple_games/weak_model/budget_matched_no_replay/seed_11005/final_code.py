def choose_move(observation):
    x, y = observation['self_position']
    width, height = observation['grid_width'], observation['grid_height']
    resources = observation.get('resources', [])
    opponent_x, opponent_y = observation['opponent_position']
    obstacles = set(tuple(obs) for obs in observation.get('obstacles', []))
    
    def safe_move(dx, dy):
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in obstacles:
            return True
        return False

    # Move towards nearest resource if any
    if resources:
        resource = min(resources, key=lambda r: abs(r[0] - x) + abs(r[1] - y))
        dx = (resource[0] - x)
        dy = (resource[1] - y)
        move_x = (1 if dx > 0 else -1) if dx != 0 else 0
        move_y = (1 if dy > 0 else -1) if dy != 0 else 0
        if safe_move(move_x, move_y):
            return [move_x, move_y]

    # Else, move towards opponent
    dx = opponent_x - x
    dy = opponent_y - y
    move_x = (1 if dx > 0 else -1) if dx != 0 else 0
    move_y = (1 if dy > 0 else -1) if dy != 0 else 0
    if safe_move(move_x, move_y):
        return [move_x, move_y]

    # Fallback: try moving right, left, down, up in order
    for dx_try, dy_try in [(1,0), (-1,0), (0,1), (0,-1)]:
        if safe_move(dx_try, dy_try):
            return [dx_try, dy_try]

    # No move possible, stay put
    return [0,0]
