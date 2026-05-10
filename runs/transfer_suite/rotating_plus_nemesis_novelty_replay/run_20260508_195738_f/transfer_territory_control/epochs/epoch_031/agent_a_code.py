def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obs = observation.get("obstacles", []) or []
    blocked = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]
    best_d = 10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            d = abs(ox - nx) + abs(oy - ny)
            if d < best_d:
                best_d = d
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]