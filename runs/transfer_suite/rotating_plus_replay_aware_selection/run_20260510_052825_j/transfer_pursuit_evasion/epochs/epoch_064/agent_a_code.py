def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    resources = observation.get("resources") or []
    tgt = None
    if resources:
        best = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if valid(rx, ry):
                    d = (sx - rx) * (sx - rx) + (sy - ry) * (sy - ry)
                    if best is None or d < best[0]:
                        best = (d, rx, ry)
        if best is not None:
            tgt = (best[1], best[2])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if tgt is None:
        tgt = (ox, oy)

    def obs_density(x, y):
        c = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if i == 0 and j == 0:
                    continue
                if (x + i, y + j) in obs:
                    c += 1
        return c

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_to_t = (nx - tgt[0]) * (nx - tgt[0]) + (ny - tgt[1]) * (ny - tgt[1])
        dist_from_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        s = -dist_to_t + 0.05 * dist_from_op - 0.3 * obs_density(nx, ny)
        if best_score is None or s > best_score:
            best_score = s
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]