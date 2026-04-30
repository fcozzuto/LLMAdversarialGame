def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obst.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if res and observation.get("remaining_resource_count", len(res)) != 0:
        best = None
        for x, y in res:
            d1 = cheb(sx, sy, x, y)
            d2 = cheb(ox, oy, x, y)
            cand = (d1, -d2, x, y)
            if best is None or cand < best:
                best = cand
        tx, ty = best[2], best[3]
    else:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = 0, 0
        best = None
        for x, y in corners:
            d = cheb(ox, oy, x, y)
            if best is None or d > best:
                best = d
                tx, ty = x, y

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer getting closer; if opponent is also close, prioritize moves that widen the gap.
        val = (myd, -opd)  # primary: my distance; secondary: opponent distance to target (smaller d is worse)
        advantage = (opd - myd)  # larger is better
        score = (val, -advantage)
        if best_val is None or score < best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]