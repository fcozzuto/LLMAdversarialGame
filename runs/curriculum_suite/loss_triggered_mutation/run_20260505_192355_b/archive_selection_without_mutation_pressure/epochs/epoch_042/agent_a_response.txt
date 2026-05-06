def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_adv = -10**9
    best_res = None
    for rx, ry in resources:
        adv = man(ox, oy, rx, ry) - man(sx, sy, rx, ry)
        if adv > best_adv:
            best_adv = adv
            best_res = (int(rx), int(ry))

    # If we aren't contesting anything better than the opponent, switch to interception.
    if best_adv < 0:
        best = None
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_opp = man(nx, ny, ox, oy)
            # Tie-break: prefer moves that also shrink distance to the opponent's nearest resource.
            opp_near = min(man(ox, oy, rx, ry) for rx, ry in resources)
            val = -d_opp * 100 - opp_near
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best is not None else [0, 0]

    # Otherwise, maximize lead on the single best resource, with a small stabilizer.
    tx, ty = best_res
    best_move = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        our_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        lead = opp_d - our_d
        # Stabilizer: don't drift away from board corners too aggressively; slight preference for lower our_d.
        score = lead * 1000 - our_d
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])] if best_move is not None else [0, 0]