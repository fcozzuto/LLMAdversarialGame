def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res = [tuple(p) for p in resources]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_target_for(me_x, me_y):
        best = None
        best_val = -10**18
        for rx, ry in res:
            md = man(me_x, me_y, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; strong boost if we can pick now.
            val = (od - md) * 10 - md
            if md == 0:
                val += 10**6
            # Slight preference for central-ish/earlier overall: lower md already in -md
            if val > best_val:
                best_val = val
                best = (rx, ry, md, od)
        return best  # (rx, ry, md, od)

    my_best_target = best_target_for(sx, sy)
    rx, ry, _, _ = my_best_target

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate how this move affects contested collection.
        target = best_target_for(nx, ny)
        tr, ty, md2, od2 = target

        # Multi-criteria: win likelihood first, then progress, then tie-break toward target (rx,ry).
        score = (od2 - md2) * 1000 - md2 * 10
        if md2 == 0:
            score += 10**7
        # If we're not heading to our currently best target, penalize slightly.
        score -= man(nx, ny, rx, ry) * 2

        # Also avoid moves that let opponent get closer to their best targets.
        # (Deterministic approximation using same resources: compute opponent best margin from current position.)
        opp_target = best_target_for(ox, oy)  # uses current opponent pos for md; od is computed against ox itself so od term cancels, but margin uses ox vs me_x
        # Recompute directly: margin for opponent over us if we don't pick instantly
        if md2 != 0:
            opp_margin = -min(man(ox, oy, r[0], r[1]) for r in res)
            score += opp_margin * 0  # keep deterministic; no extra computation dominance

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move