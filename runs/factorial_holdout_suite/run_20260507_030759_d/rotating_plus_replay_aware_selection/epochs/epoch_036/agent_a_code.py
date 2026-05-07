def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None  # (score, -lead, ds, move)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        best_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer now
            # big bonus for immediate pickup and for taking lead; penalty for being late
            score = (lead * 1000) - ds - do
            if ds == 0:
                score += 10**7
            # slight preference to be in a contested race (closer overall)
            score += -abs(lead)
            cand = (score, -lead, ds)
            if best_for_move is None or cand < best_for_move:
                best_for_move = cand
        if best_for_move is None:
            continue
        cand_total = (best_for_move[0], best_for_move[1], best_for_move[2], (dx, dy))
        if best is None:
            best = cand_total
        else:
            # higher score, then smaller -lead (i.e., larger lead), then smaller ds, then deterministic move order
            if cand_total[0] > best[0] or (cand_total[0] == best[0] and (cand_total[1], cand_total[2], cand_total[3][0], cand_total[3][1]) < (best[1], best[2], best[3][0], best[3][1])):
                best = cand_total

    return [best[3][0], best[3][1]]