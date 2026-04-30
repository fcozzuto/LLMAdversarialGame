def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obst = set((p[0], p[1]) for p in obstacles)

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    res_set = set((r[0], r[1]) for r in resources)
    if not res_set:
        tx, ty = (w - 1, h - 1) if sx + sy < ox + oy else (0, 0)
    else:
        best = None
        best_val = -10**9
        for rx, ry in res_set:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = (do - ds) * 10 - ds  # prioritize resources closer than opponent
            if val > best_val:
                best_val = val
                best = (rx, ry)
            elif val == best_val:
                if ds < cheb(sx, sy, best[0], best[1]):
                    best = (rx, ry)
        tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_ds = cheb(sx, sy, tx, ty)
    cur_do = cheb(ox, oy, sx, sy)

    best_m = [0, 0]
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        score = 0
        if (nx, ny) in res_set:
            score += 100000
        score += (cur_ds - nds) * 50
        score += (ndo - ndo)  # no change; keep deterministic placeholder at 0
        score += (cur_do - cheb(ox, oy, nx, ny)) * 3  # mildly prefer moving away from opponent distance
        score += -(abs(nx - tx) + abs(ny - ty)) * 0.01
        if score > best_score:
            best_score = score
            best_m = [dx, dy]

    return best_m