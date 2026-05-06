def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        # Deterministic fallback: drift toward center to reduce denier effectiveness.
        tx, ty = w // 2, h // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = -(man(nx, ny, tx, ty))
                if v > bestv:
                    bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Pick a target resource to either secure or deny.
    # If we can already beat the opponent on some resource, target the closest such one.
    best_target = None
    best_target_key = None
    for rx, ry in resources:
        od = man(ox, oy, rx, ry)
        sd = man(sx, sy, rx, ry)
        row_gap = abs(sy - ry)
        # Key: prefer (sd <= od), then minimize sd, tie-break by row closeness.
        can_secure = 1 if sd <= od else 0
        key = (can_secure, -row_gap, -sd)
        if best_target is None or key > best_target_key:
            best_target, best_target_key = (rx, ry), key

    rx, ry = best_target
    # If we cannot secure any, deny: move toward the resource where opponent is most ahead.
    if best_target_key[0] == 0:
        best2 = None
        bestk = None
        for r2x, r2y in resources:
            od = man(ox, oy, r2x, r2y)
            sd = man(sx, sy, r2x, r2y)
            lead = od - sd  # positive means opponent ahead
            key = (lead, -abs(sy - r2y), -sd)
            if best2 is None or key > bestk:
                best2, bestk = (r2x, r2y), key
        rx, ry = best2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)
        # Advantage: positive if we reduce opponent lead. Add row alignment to maintain denial pressure.
        adv = (od - sd)
        row_bonus = 3 if ny == ry else (2 if abs(ny - ry) == 1 else (1 if abs(ny - ry) == 2 else 0))
        # Secondary objective: reduce distance to any resource we can potentially secure next.
        near = 10**9
        for r2x, r2y in resources:
            nd = man(nx, ny, r2x, r2y)
            if nd < near:
                near = nd
        val = adv * 10 + row_bonus * 2 - near * 0.01
        if val > best_val:
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]