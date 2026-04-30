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

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    t = int(observation.get("turn_index") or 0)
    late = 1 if t > 45 else 0
    side_bias = 0 if w <= 0 else 1
    # agent_b tends to be in top-right; prefer resources with larger x,y in late game
    def side_score(rx, ry):
        return (rx + ry) if late else 0

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # race heuristic: maximize (opp_dist - my_dist) to a chosen resource
        # late: slightly prefer pushing into higher (x+y) resources
        best_adv = -10**18
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            if late:
                val = (opd - myd) + 0.02 * side_score(rx, ry) - 0.001 * myd
            else:
                val = (opd - myd) - 0.001 * myd
            if val > best_adv:
                best_adv = val

        # if no visible resources, move to reduce distance to center deterministically
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            best_adv = -man(nx, ny, cx, cy)

        # prefer staying when equal, but deterministic: lexicographic by fixed order already
        if best_adv > best_val:
            best_val = best_adv
            best = [dx, dy]

    return best