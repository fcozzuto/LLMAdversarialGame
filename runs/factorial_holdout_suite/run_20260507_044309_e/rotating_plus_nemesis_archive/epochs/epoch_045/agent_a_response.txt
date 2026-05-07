def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for b in obstacles:
        if b is None or len(b) < 2:
            continue
        bx, by = int(b[0]), int(b[1])
        if 0 <= bx < w and 0 <= by < h:
            blocked.add((bx, by))

    res = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
            res.append((rx, ry))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    best = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate by how much we improve our advantage to the most "contested" resource.
        # Score favors: (op_dist - self_dist) on a target, then staying safe-ish (avoid proximity to obstacles edges not needed), then tie-break by self distance.
        local_best = -10**18
        local_self_d = 10**9
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer to that resource than opponent currently
            val = adv * 100 - sd  # strong preference for contested steals; then closeness
            if val > local_best:
                local_best = val
                local_self_d = sd

        # Small secondary term: if opponent could reach a resource immediately, prefer delaying by moving away from their best target
        # (deterministic, cheap approximation).
        away = 0
        for rx, ry in res:
            sd_o = cheb(ox, oy, rx, ry)
            if sd_o == 0:
                # opponent already on a resource (rare); move to maximize distance from that cell
                away = max(away, cheb(nx, ny, rx, ry))
            else:
                break

        total = local_best + away
        if total > best_score:
            best_score = total
            best = [dx, dy]
        elif total == best_score:
            # Deterministic tie-break: prefer moves that reduce our distance to any resource; then lexicographic dx,dy
            if local_self_d < cheb(sx, sy, best and sx or sx, sy):
                best = [dx, dy]
            elif (dx, dy) < (best[0], best[1]):
                best = [dx, dy]

    return best