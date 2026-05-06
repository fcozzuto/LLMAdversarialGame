def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # 1-step minimax-ish: choose move that maximizes our best advantage while limiting opponent's best advantage
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep us; mirror that deterministically

        # Our target: resource that gives max advantage after the move
        best_our = -10**18
        best_opp_for_that = 10**18
        for tx, ty in res:
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)
            adv = opd - myd
            # tie-break to prefer closer-to-reach for us
            if adv > best_our or (adv == best_our and myd < best_opp_for_that):
                best_our = adv
                best_opp_for_that = myd

        # Opponent's potential: best advantage they currently have (proxy for denying pressure)
        best_opp = -10**18
        for tx, ty in res:
            myd = md(ox, oy, tx, ty)
            opd = md(nx, ny, tx, ty)  # compare against our current prospective position
            opp_adv = opd - myd
            if opp_adv > best_opp:
                best_opp = opp_adv

        # Additional shaping: avoid moving away from the nearest resource
        nearest = min(res, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
        cur_dn = md(nx, ny, nearest[0], nearest[1])

        val = best_our * 1000 - cur_dn * 2 - best_opp * 300
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # deterministic tie-break: lexicographically smallest (dx,dy)
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]