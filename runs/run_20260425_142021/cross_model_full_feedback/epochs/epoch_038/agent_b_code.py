def choose_move(observation):
    x, y = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # 1) Move toward the closest resource not blocked by obstacles
    if resources:
        best = None
        best_dist = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = abs(rx - x) + abs(ry - y)
            if best_dist is None or d < best_dist:
                best_dist = d
                best = (rx, ry)
        if best is not None:
            rx, ry = best
            dx = 0 if rx == x else (1 if rx > x else -1)
            dy = 0 if ry == y else (1 if ry > y else -1)
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]

    # 2) Move toward opponent if possible
    oppx, oppy = observation["opponent_position"]
    dx = 0 if oppx == x else (1 if oppx > x else -1)
    dy = 0 if oppy == y else (1 if oppy > y else -1)
    nx, ny = x + dx, y + dy
    if in_bounds(nx, ny) and (nx, ny) not in obstacles:
        return [dx, dy]

    # 3) Fallback: explore in a fixed order, excluding staying put if possible
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    for ddx, ddy in directions:
        nx, ny = x + ddx, y + ddy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            return [ddx, ddy]

    # If all else fails, stay
    return [0, 0]