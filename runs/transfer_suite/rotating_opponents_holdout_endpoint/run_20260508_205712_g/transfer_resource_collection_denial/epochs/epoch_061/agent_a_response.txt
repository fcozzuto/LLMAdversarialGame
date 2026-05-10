def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            val = -man(nx, ny, ox, oy)  # maximize distance from opponent
            k = (-val, nx, ny)
            if best is None or k < best[0]:
                best = (k, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Pick a target resource where we are relatively closer, but also prefer being close.
    best_t = None
    best_k = None
    for rx, ry in resources:
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        adv = opp_d - self_d  # larger means we are closer
        val = adv * 1000 - self_d  # deterministic preference
        k = (-val, self_d, rx, ry)
        if best_k is None or k < best_k:
            best_k = k
            best_t = (rx, ry)

    tx, ty = best_t

    # Choose step that maximizes advantage for that target after the move.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_d2 = man(nx, ny, tx, ty)
        opp_d2 = man(ox, oy, tx, ty)
        adv2 = opp_d2 - self_d2
        # slight tie-break to keep progressing toward target
        val = adv2 * 1000 - self_d2
        k = (-val, self_d2, ny, nx, dx, dy)
        if best is None or k < best[0]:
            best = (k, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]