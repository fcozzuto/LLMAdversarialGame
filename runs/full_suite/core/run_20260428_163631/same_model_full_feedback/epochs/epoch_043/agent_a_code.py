def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def score_cell(nx, ny):
        best_r = 10**9
        for rx, ry in resources:
            d = abs(nx - rx) + abs(ny - ry)
            if d < best_r:
                best_r = d
        if resources:
            res_part = best_r
        else:
            cx, cy = w // 2, h // 2
            res_part = abs(nx - cx) + abs(ny - cy)
        opp_dist = abs(nx - ox) + abs(ny - oy)
        if resources:
            return res_part * 10 - opp_dist
        return res_part - opp_dist

    best = None
    best_val = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = score_cell(nx, ny)
        if v < best_val:
            best_val = v
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]