def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    dirs.append((0, 0))

    # Prefer unclaimed cells that are next to opponent territory (edge-claim counters).
    def adj_opp(p):
        x, y = p
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in opp_t:
                    return 1
        return 0

    if unclaimed:
        cand = sorted(unclaimed, key=lambda p: (-adj_opp(p), abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        tx, ty = cand[0]
    elif opp_t:
        cand = sorted(opp_t, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        tx, ty = cand[0]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    def cell_gain(nx, ny):
        if (nx, ny) in opp_t:
            return 120  # likely flip control on entry
        if (nx, ny) in unclaimed:
            return 10
        if (nx, ny) in self_t:
            return 6
        return 1

    def threat(nx, ny):
        # Avoid stepping too deep into opponent-held area unless we can flip it.
        # Use min Chebyshev distance to opponent territory.
        best = 999
        for (ox, oy) in opp_t:
            d = max(abs(ox - nx), abs(oy - ny))
            if d < best:
                best = d
        if not opp_t:
            return 0
        return -min(best, 6)  # closer to opp => worse

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Two-ply deterministic lookahead toward (tx,ty): choose locally best next step after this move.
        d1 = abs(tx - nx) + abs(ty - ny)
        val = cell_gain(nx, ny) + threat(nx, ny) - 0.6 * d1
        # small second-step bonus if next step reduces distance quickly
        step2_best = 0
        for ddx, ddy in dirs:
            mx, my = nx + ddx, ny + ddy
            if not ok(mx, my):
                continue
            gain2 = cell_gain(mx, my) - 0.4 * (abs(tx - mx) + abs(ty - my))
            if gain2 > step2_best:
                step2_best = gain2
        val += 0.25 * step2_best

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]