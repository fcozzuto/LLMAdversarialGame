def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        dx = 0 if abs(sx - tx) < 0.5 else (1 if tx > sx else -1)
        dy = 0 if abs(sy - ty) < 0.5 else (1 if ty > sy else -1)
        return [int(dx), int(dy)]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def next_risk(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return 10**9
        r = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (nx + ddx, ny + ddy) in obstacles:
                    r += 1
        return r

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        risk = next_risk(nx, ny)
        if risk >= 10**8:
            continue

        myd = cheb(nx, ny, sx, sy)  # always 1/0/diagonal; keeps deterministic small variation
        val = -0.01 * myd - 0.9 * risk

        # Choose the best resource target according to relative closeness vs opponent.
        for tx, ty in resources:
            if (tx, ty) in obstacles:
                continue
            myd_t = cheb(nx, ny, tx, ty)
            opd_t = cheb(ox, oy, tx, ty)
            rel = (opd_t - myd_t)  # positive => we are closer
            dist_center = abs(tx - cx) + abs(ty - cy)

            # Strong preference for taking resources before opponent; mild preference for center.
            score = 6.0 * rel - 0.05 * dist_center - 0.02 * myd_t

            # If we can reach in one step, spike.
            if myd_t == 0:
                score += 60.0
            elif myd_t == 1:
                score += 18.0

            # If opponent can also reach next, reduce relative benefit (still deterministic).
            if opd_t <= 1:
                score -= 4.0

            if score > val:
                val = score

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]