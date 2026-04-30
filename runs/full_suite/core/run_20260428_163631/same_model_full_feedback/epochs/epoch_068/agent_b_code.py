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

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = (10**9, 10**9)
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d_opp = cheb((nx, ny), (ox, oy))
            d_self = 0
            cand = (d_opp, -d_self)
            if cand > best:
                best = cand
                best_move = [dx, dy]
        return best_move

    best_score = None
    target = resources[0]
    for r in resources:
        d1 = cheb((sx, sy), r)
        d2 = cheb((ox, oy), r)
        score = (d1 - d2, d1)  # prioritize being closer than opponent; then closer overall
        if best_score is None or score < best_score:
            best_score = score
            target = r

    tx, ty = target
    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_next = cheb((nx, ny), (tx, ty))
        d_opp_next = cheb((nx, ny), (ox, oy))
        cand = (d_next, d_opp_next)  # primarily minimize distance to target; then avoid opponent
        if best is None or cand < best:
            best = cand
            best_move = [dx, dy]
    return best_move