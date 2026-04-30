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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target(px, py):
        if not resources:
            return (w // 2, h // 2)
        best = resources[0]
        best_gain = -10**9
        for tx, ty in resources:
            sd = cheb(px, py, tx, ty)
            od = cheb(ox, oy, tx, ty)
            gain = od - sd  # positive means we are closer than opponent
            if gain > best_gain:
                best_gain = gain
                best = (tx, ty)
        return best

    tx, ty = best_target(sx, sy)

    # Choose move that improves our distance to chosen target; break ties by improving gain vs opponent.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        curd = cheb(sx, sy, tx, ty)
        improved = curd - myd
        oppd = cheb(ox, oy, tx, ty)
        gain = oppd - myd
        score = (improved * 1000) + gain
        if (score > best_score) or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]