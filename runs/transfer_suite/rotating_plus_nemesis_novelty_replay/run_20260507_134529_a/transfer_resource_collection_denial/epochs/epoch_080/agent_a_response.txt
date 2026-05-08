def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    blocked = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    resources = observation.get("resources") or []

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        # Two-ply greedy: pick move that minimizes our distance to a strong target,
        # while maximizing the advantage over opponent (deny-first).
        best_s = None
        best_mv = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # avoid stepping onto positions that are bad for next step only if alternatives exist
            worst_penalty = 0
            for sx2, sy2 in [(nx, ny)]:
                # evaluate by best target for us (with deny component)
                best_t = None
                for r in resources:
                    rx, ry = r[0], r[1]
                    rprio = r[2] if len(r) > 2 else 1
                    d_self = man(sx2, sy2, rx, ry)
                    d_opp = man(ox, oy, rx, ry)
                    # deny: prefer targets where we are closer than opponent
                    deny = (d_opp - d_self)
                    # score smaller is better
                    val = d_self - 0.8 * deny - 0.05 * rprio + 0.02 * man(nx, ny, ox, oy)
                    if best_t is None or val < best_t:
                        best_t = val
                worst_penalty += best_t
            s = worst_penalty
            if best_s is None or s < best_s or (s == best_s and (dx, dy) < tuple(best_mv)):
                best_s = s
                best_mv = [dx, dy]
        return best_mv

    # No resources: deterministic orbit/intercept. Go toward the midpoint that reduces distance to both.
    tx = (sx + ox) // 2
    ty = (sy + oy) // 2
    # If the midpoint is blocked/out, head directly to opponent corner first.
    target_x, target_y = (tx, ty)
    if not free(target_x, target_y):
        target_x, target_y = (ox, oy)

    best_d = None
    best_mv = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = man(nx, ny, target_x, target_y)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < tuple(best_mv)):
            best_d = d
            best_mv = [dx, dy]
    return best_mv