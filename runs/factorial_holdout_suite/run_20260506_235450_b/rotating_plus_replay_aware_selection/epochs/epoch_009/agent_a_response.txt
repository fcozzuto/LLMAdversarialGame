def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # Move to reduce distance to opponent (simple pressure)
        best = None
        for dx, dy, nx, ny in legal:
            v = (man(nx, ny, ox, oy), man(nx, ny, sx, sy))
            if best is None or v < best[0]:
                best = (v, (dx, dy))
        return list(best[1])

    best_target = None  # (win_flag, score, self_dist, rx, ry)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        win_flag = 0 if ds <= do else 1
        score = (do - ds) - 0.1 * ds  # favor bigger race advantage, then closeness
        key = (win_flag, -score, ds, rx, ry)
        if best_target is None or key < best_target:
            best_target = key

    _, _, _, tx, ty = best_target

    # Choose move: prefer stepping closer to target; if tie, prefer closer to target over opponent
    best_move = None  # (key, (dx,dy))
    for dx, dy, nx, ny in legal:
        ds2 = man(nx, ny, tx, ty)
        do2 = man(nx, ny, ox, oy)
        toward = ds2
        race = (1 if ds2 > do2 else 0)  # want ds2 <= do2 => 0
        key = (race, toward, -do2, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, (dx, dy))
    return [best_move[1][0], best_move[1][1]]