def choose_move(observation):
    # Deterministic agent: move towards the nearest resource if available,
    # otherwise approach the opponent (to contest) or stay if blocked by bounds.

    x, y = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))
    
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # If there is a resource not on an obstacle, target the closest one
    best_move = (0, 0)
    if resources:
        # Find closest resource by Manhattan distance
        best_r = None
        best_d = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = abs(rx - x) + abs(ry - y)
            if best_d is None or d < best_d:
                best_d = d
                best_r = (rx, ry)
        if best_r is not None:
            rx, ry = best_r
            dx = 0 if rx == x else (1 if rx > x else -1)
            dy = 0 if ry == y else (1 if ry > y else -1)
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]

    # If no resource or blocked path, move toward opponent to contest
    oppx, oppy = observation["opponent_position"]
    dx = 0 if oppx == x else (1 if oppx > x else -1)
    dy = 0 if oppy == y else (1 if oppy > y else -1)
    nx, ny = x + dx, y + dy
    if in_bounds(nx, ny) and (nx, ny) not in obstacles:
        return [dx, dy]

    # If cannot move toward resource or opponent due to obstacles/bounds, try to stay or take a safe step
    # Try all 8 directions to find any valid move (deterministic order)
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 0), (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    for ddx, ddy in directions:
        nx, ny = x + ddx, y + ddy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            # Ensure we do not move outside; prefer non-zero move if possible
            if not (ddx == 0 and ddy == 0):
                return [ddx, ddy]
            # fallback to staying still
            return [0, 0]

    # If everything blocked (shouldn't happen), stay
    return [0, 0]