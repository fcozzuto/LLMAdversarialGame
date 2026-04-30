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
    resources = list(set(resources))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def target_value(tx, ty):
        d_me = cheb(sx, sy, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Prefer targets where we have an arrival lead; tie-break by closeness to us.
        return (d_op - d_me) * 1000 - d_me

    tx, ty = None, None
    if resources:
        bestv = -10**18
        for rx, ry in resources:
            v = target_value(rx, ry)
            if v > bestv or (v == bestv and (rx, ry) < (tx, ty)):
                bestv = v
                tx, ty = rx, ry

    if tx is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, cx, cy) - 0.01 * cheb(nx, ny, ox, oy)
            if v > best[0]:
                best = (v, dx, dy)
        return [int(best[1]), int(best[2])]

    cur_margin = cheb(ox, oy, tx, ty) - cheb(sx, sy, tx, ty)

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Primary: maximize our advantage to the chosen target next step.
        score = (d_op - d_me) * 2000
        # Secondary: reduce our distance to that target.
        score -= d_me * 10
        # Tertiary: if we might be losing, avoid moves that let opponent closer to remaining resources.
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            score += (do - dm) * 3
        # Light discourage moving into bad relative states.
        if cur_margin < 0:
            score -= cheb(nx, ny, ox, oy)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]