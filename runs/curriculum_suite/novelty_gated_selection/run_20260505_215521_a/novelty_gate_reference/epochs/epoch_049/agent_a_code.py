def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax, ay = x1 - x2, y1 - y2
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    # Novelty: choose move by maximizing "possession advantage" over the nearest-resource opponent,
    # while also preferring closer-to-us targets to keep tempo.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose a single target deterministically: among resources, pick the one where we gain most.
        # Then evaluate that target for this move.
        local_best_adv = None
        local_best_td = None
        for rx, ry in resources:
            d_us = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Advantage if we reach earlier; also slight preference for nearer targets for immediate momentum.
            adv = (d_opp - d_us) * 10 - d_us
            # Tie-break deterministically by coordinates
            td = (adv, -rx, -ry)
            if local_best_adv is None or td > (local_best_td[0], local_best_td[1], local_best_td[2]):
                local_best_adv = adv
                local_best_td = td

        if local_best_adv is None:
            continue

        # Prefer moves that keep us safe from "being too late" even if advantage is similar.
        late_pen = 0
        for rx, ry in resources:
            d_us = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_us > d_opp + 2:
                late_pen += 1

        key = (local_best_adv, -late_pen, -cheb(nx, ny, ox, oy), dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best else [0, 0]