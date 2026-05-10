def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    best = None  # (max_adv, -best_sd, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        local_best_sd = None
        local_best_adv = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if not ok(rx, ry) and (rx, ry) not in resources:
                continue
            sd = md(nx, ny, rx, ry)
            if sd is None:
                continue
            od = md(ox, oy, rx, ry)
            adv = od - sd
            if local_best_adv is None or adv > local_best_adv or (adv == local_best_adv and (local_best_sd is None or sd < local_best_sd)):
                local_best_adv = adv
                local_best_sd = sd
        if local_best_adv is None:
            continue
        cand = (local_best_adv, -(local_best_sd if local_best_sd is not None else 10**9), dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[2], best[3]]