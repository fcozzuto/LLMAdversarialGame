def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list if p is not None and len(p) >= 2}

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # For this candidate cell, consider all resources; prioritize ones where we are (or become) closer than opponent.
        local_best_gain = -10**9
        local_best_selfd = 10**9
        local_best_oppd = 10**9
        for r in resources:
            rx, ry = r[0], r[1]
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            gain = od - sd
            # deterministic tie-breaking using resource coordinates
            if (gain > local_best_gain or
                (gain == local_best_gain and (sd < local_best_selfd or (sd == local_best_selfd and (od < local_best_oppd or (od == local_best_oppd and (rx, ry) < res_t)))))):
                local_best_gain = gain
                local_best_selfd = sd
                local_best_oppd = od
                res_t = (rx, ry)
        # Prefer moves that (1) secure closeness advantage, (2) make faster progress, (3) reduce opponent's access.
        # If gain is negative for all resources, we still go toward nearest while keeping opponent distance low as a backup.
        opp_nearest_after = min(md(ox, oy, r[0], r[1]) for r in resources)
        self_nearest_after = min(local_best_selfd, min(md(nx, ny, r[0], r[1]) for r in resources))
        score = (-local_best_gain, self_nearest_after, opp_nearest_after, dx, dy)
        if best is None or score < best:
            best = score
    return [best[3], best[4]] if best is not None else [0, 0]