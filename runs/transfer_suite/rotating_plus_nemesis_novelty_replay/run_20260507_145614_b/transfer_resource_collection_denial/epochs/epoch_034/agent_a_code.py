def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    resources = observation.get("resources", []) or []
    if resources:
        best = None
        for rx, ry in resources:
            dso = abs(ox - rx) + abs(oy - ry)
            dss = abs(sx - rx) + abs(sy - ry)
            val = (dso - dss, -abs(sx - rx) - abs(sy - ry), -rx, -ry)
            if best is None or val > best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_opp = abs(ox - tx) + abs(oy - ty)
        d_self = abs(nx - tx) + abs(ny - ty)
        val = (d_opp - d_self, -d_self, -nx, -ny)
        if best_move is None or val > best_move[0]:
            best_move = (val, [dx, dy])
    return best_move[1] if best_move is not None else [0, 0]