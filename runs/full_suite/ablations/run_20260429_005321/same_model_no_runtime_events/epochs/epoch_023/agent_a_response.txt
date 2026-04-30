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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        # Choose target where we are closer than opponent, and where that lead is largest.
        best_t = None
        best_gain = -10**18
        for x, y in resources:
            sd = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            # Prefer immediate advantage; mild tie-break by preferring nearer overall.
            gain = (od - sd) * 1000 - sd
            if gain > best_gain:
                best_gain = gain
                best_t = (x, y)
        tx, ty = best_t
    else:
        # No visible resources: head to center while keeping away from obstacles via valid moves.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # One-step greedy: pick move that minimizes distance to target; tie-break by maximizing (opponent - self).
    best_move = [0, 0]
    best_d = 10**9
    best_adv = -10**18
    # Deterministic tie-breaking order: use dirs in listed order.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        sd = d
        od = cheb(ox, oy, tx, ty)
        adv = od - sd
        if d < best_d or (d == best_d and (adv > best_adv)):
            best_d = d
            best_adv = adv
            best_move = [dx, dy]

    return best_move