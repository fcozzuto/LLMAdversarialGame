def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        # Fallback: head toward opponent's corner to contest, unless blocked.
        target = (0, h - 1) if (sx + sy) % 2 == 0 else (w - 1, 0)
    else:
        # Choose resource where we are relatively closer; penalize those aligned with opponent.
        best_key = None
        target = resources[0]
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            advantage = od - sd  # higher means we are closer
            align_pen = 0
            if ry == oy:
                align_pen += 4
            elif abs(ry - oy) == 1:
                align_pen += 2
            if rx == ox:
                align_pen += 3
            elif abs(rx - ox) == 1:
                align_pen += 1
            edge_bias = 0
            if rx in (0, w - 1) or ry in (0, h - 1):
                edge_bias = 0.5  # mild determinism preference
            key = (-advantage + align_pen + edge_bias, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                target = (rx, ry)

    tx, ty = target
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer reducing distance to target; also avoid moving into opponent's likely sweep axis.
        d_now = man(sx, sy, tx, ty)
        d_next = man(nx, ny, tx, ty)
        dist_improve = d_now - d_next  # higher better
        # If we move to align with opponent, discount.
        align = 0
        if ny == oy:
            align += 3
        elif abs(ny - oy) == 1:
            align += 1
        if nx == ox:
            align += 2
        elif abs(nx - ox) == 1:
            align += 1
        # Small tie-breaker: deterministic lexicographic order via dx,dy.
        score = (dist_improve - 0.4 * align, -d_next, -man(nx, ny, ox, oy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]