def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        # diagonal-allowed shortest path length with only step deltas
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res_list = [tuple(p) for p in resources]
    res_set = set(res_list)

    best = None
    best_val = -10**18

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue

        val = 0
        if (nx, ny) in res_set:
            val += 1000

        # race to the most favorable resource
        local_best = -10**18
        for i, r in enumerate(res_list):
            myd = dist((nx, ny), r)
            opd = dist((ox, oy), r)
            if myd < opd:
                s = (opd - myd) * 35 + (50 - myd) + (1.0 / (i + 1))
            elif myd == opd:
                s = 10 + (1.0 / (i + 1))
            else:
                s = -(myd - opd) * 20 - myd * 0.2 + (1.0 / (i + 1))
            if s > local_best:
                local_best = s
        val += local_best

        # mild anti-stall: prefer progress
        val -= 0.5 * dist((nx, ny), (w - 1, h - 1))

        tie = (nx, ny)
        if val > best_val or (val == best_val and (best is None or tie < best)):
            best_val = val
            best = tie
            best_move = (mx, my)

    if best is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]