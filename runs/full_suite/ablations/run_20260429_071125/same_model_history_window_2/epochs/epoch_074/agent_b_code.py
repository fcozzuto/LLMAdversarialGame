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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any(x == sx and y == sy for x, y in resources):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target():
        if not resources:
            return None
        best = None
        bd = 10**9
        bo = -10**9
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            do = cheb(x, y, ox, oy)
            keyd = d
            keyo = do
            if keyd < bd or (keyd == bd and keyo > bo):
                bd, bo, best = keyd, keyo, (x, y)
        return best

    target = best_target()

    # Choose move by minimizing distance to target, maximizing distance from opponent.
    best_move = [0, 0]
    best_score = -10**18
    if target is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty) + 0.1 * cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        # Prefer reaching resource sooner; break ties by keeping away from opponent.
        score = -d * 100 + do
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]