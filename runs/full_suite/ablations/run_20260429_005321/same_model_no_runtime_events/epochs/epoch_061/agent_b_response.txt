def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # Drift toward center while keeping distance from opponent.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -dist_manh((nx, ny), (cx, cy)) + 0.2 * dist_manh((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    # Choose target resource where our advantage (us closer than opponent) is largest.
    best_target = None
    best_adv = -10**18
    for rx, ry in resources:
        du = dist_manh((sx, sy), (rx, ry))
        do = dist_manh((ox, oy), (rx, ry))
        adv = do - du  # positive if we are closer
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    # Evaluate next move: reduce disadvantage to target; also avoid moving toward opponent unnecessarily.
    tx, ty = best_target
    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        cur_d = dist_manh((sx, sy), (tx, ty))
        nxt_d = dist_manh((nx, ny), (tx, ty))
        opp_d_cur = dist_manh((ox, oy), (tx, ty))
        # Approximate opponent pressure: if our move makes target more reachable to them, slightly penalize.
        opp_d_nxt = opp_d_cur - (0 if nxt_d >= cur_d else 0)
        v = (cur_d - nxt_d) * 100.0  # primary: go toward target
        v -= nxt_d * 2.0
        v += dist_manh((nx, ny), (ox, oy)) * 0.25  # secondary: keep some separation
        v -= max(0, (opp_d_nxt - nxt_d)) * 0.5
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return list(best) if best is not None else [0, 0]