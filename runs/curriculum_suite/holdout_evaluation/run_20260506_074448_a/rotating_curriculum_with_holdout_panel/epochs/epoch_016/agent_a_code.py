def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def interior_pen(x, y):
        d = x
        t = w - 1 - x
        if t < d:
            d = t
        t = y
        if t < d:
            d = t
        t = h - 1 - y
        if t < d:
            d = t
        return d  # higher means more interior

    best_dx, best_dy = 0, 0
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best = -10**9
        my_any = False
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Encourage getting closer than opponent; also reward going for nearer resources
            val = (od - myd) * 100 - myd
            if val > my_best:
                my_best = val
            my_any = True

        if not my_any:
            continue

        # Prefer moderately interior positions; discourage standing on edges too long
        edge = interior_pen(nx, ny)
        score = my_best + (edge * 2)

        # Deterministic tie-break: prefer smallest |dx|+|dy| then lexicographic
        if best_score is None or score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy
        elif score == best_score:
            cur_m = abs(dx) + abs(dy)
            best_m = abs(best_dx) + abs(best_dy)
            if cur_m < best_m or (cur_m == best_m and (dx, dy) < (best_dx, best_dy)):
                best_dx, best_dy = dx, dy

    return [best_dx, best_dy]