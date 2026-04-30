def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = md(nx, ny, cx, cy)
            if v < best[0] or (v == best[0] and (nx, ny) < best[1]):
                best = (v, (nx, ny))
        nx, ny = best[1]
        return [nx - sx, ny - sy]

    # Greedy evaluation of next position: prefer states where we are closer to resources than opponent.
    best_move = (-(10**18), None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Multi-resource value: choose best resource target, then small bias toward being generally closer.
        my_best = 10**9
        opp_best = 10**9
        target_bonus = 0
        for rx, ry in resources:
            m = md(nx, ny, rx, ry)
            o = md(ox, oy, rx, ry)
            if m < my_best:
                my_best = m
                opp_best = o
                target_bonus = (o - m)
            elif o - m > target_bonus:
                target_bonus = o - m
        # If we can grab a resource immediately, prioritize heavily.
        immediate = 1 if (nx, ny) in resources else 0
        # Also avoid moves that allow opponent to be strictly closer to any resource by a wide margin.
        opp_lead = 0
        for rx, ry in resources:
            m = md(nx, ny, rx, ry)
            o = md(ox, oy, rx, ry)
            if o + 1 < m:
                opp_lead = max(opp_lead, o - m)
        val = 1000000 * immediate + 50 * target_bonus - 3 * my_best + 2 * (-opp_lead)
        key = (val, -md(nx, ny, ox, oy), -nx, -ny)
        if best_move[1] is None or key > best_move[0]:
            best_move = (key, (nx, ny))

    nx, ny = best_move[1]
    return [nx - sx, ny - sy]