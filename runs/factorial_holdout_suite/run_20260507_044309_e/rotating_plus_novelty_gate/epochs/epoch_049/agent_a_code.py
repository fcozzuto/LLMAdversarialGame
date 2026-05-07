def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy
    resources = observation.get("resources", []) or []
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]
    if not resources:
        tx, ty = w // 2, h // 2
        best = min(valid, key=lambda m: (md(m[2], m[3], tx, ty), valid.index(m)))
        return [best[0], best[1]]

    res = [tuple(r) for r in resources]
    # Opponent target = their nearest resource (tie by index)
    opp_idx = min(range(len(res)), key=lambda i: (md(ox, oy, res[i][0], res[i][1]), i))
    opp_t = res[opp_idx]
    t0 = opp_t[0], opp_t[1]
    d_opp = md(ox, oy, t0[0], t0[1])

    # If we can reach opponent's target no later, try to block it.
    my_d = md(sx, sy, t0[0], t0[1])
    if my_d <= d_opp:
        target = t0
    else:
        # Otherwise pick a resource where we have the largest advantage over opponent.
        best_score = None
        best_r = res[0]
        for rx, ry in res:
            my = md(sx, sy, rx, ry)
            opp = md(ox, oy, rx, ry)
            adv = opp - my  # higher means more likely we arrive first
            key = (-(adv), my, opp)  # deterministic tie-break
            if best_score is None or key < best_score:
                best_score = key
                best_r = (rx, ry)
        target = best_r

    tx, ty = target
    # Choose move that minimizes distance to chosen target, with tie-break against opponent target.
    sec_dx, sec_dy = t0
    def move_key(m):
        nx, ny = m[2], m[3]
        d1 = md(nx, ny, tx, ty)
        # Secondary: if opponent target is same, also minimize our distance there (stability)
        d2 = md(nx, ny, sec_dx, sec_dy)
        # Tertiary: prefer steps that reduce our distance to any resource (avoid stalling)
        d_any = min(md(nx, ny, r[0], r[1]) for r in res)
        return (d1, d2, d_any, valid.index(m))
    best = min(valid, key=move_key)
    return [best[0], best[1]]