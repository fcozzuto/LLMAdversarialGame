def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    res_list = [tuple(p) for p in resources if 0 <= p[0] < w and 0 <= p[1] < h and tuple(p) not in obstacles]
    if not res_list:
        dx = 0; dy = 0
        if sx < w - 1: dx = 1
        elif sy < h - 1: dy = 1
        return [dx, dy]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def best_for_pos(px, py):
        bestv = -10**9; tie = None
        for rx, ry in res_list:
            sd = dist((px, py), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # Prefer resources closer than opponent; tie-break by overall closeness to reduce dithering
            v = (od - sd) * 10 - sd
            if v > bestv:
                bestv = v; tie = (rx, ry)
        return bestv, tie

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        sc, _ = best_for_pos(nx, ny)
        if sc > best_score:
            best_score = sc; best_move = (dx, dy)
        elif sc == best_score:
            # Deterministic tie-breaker: lexicographic preference closer to center
            cx, cy = (w - 1) / 2, (h - 1) / 2
            curd = abs((sx + best_move[0]) - cx) + abs((sy + best_move[1]) - cy)
            newd = abs(nx - cx) + abs(ny - cy)
            if newd < curd:
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]