def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if res:
        best_r = None
        best_v = -10**18
        for r in res:
            rx, ry = r
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            v = (do - ds) - 0.1 * ds  # prefer resources opponent is less able to reach
            if v > best_v:
                best_v = v
                best_r = (rx, ry)
    else:
        best_r = None

    best_move = (0, 0)
    best_score = -10**18
    if best_r is None:
        target = (ox, oy)
    else:
        target = best_r

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dnt = dist(nx, ny, target[0], target[1])
        if best_r is None:
            score = -dnt
        else:
            ds = dnt
            do = dist(ox, oy, target[0], target[1])
            score = (do - ds) - 0.15 * ds + 0.05 * dist(nx, ny, ox, oy)
        if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]