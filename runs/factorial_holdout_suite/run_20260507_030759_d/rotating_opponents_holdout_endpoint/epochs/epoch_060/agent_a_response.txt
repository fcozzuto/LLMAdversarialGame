def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                valid_res.append((x, y))
    if not valid_res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, cx, cy)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    best_target = None
    for tx, ty in valid_res:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        score = (do - ds, -ds, tx, ty)
        if best_target is None or score > best_target[0]:
            best_target = (score, (tx, ty))
    tx, ty = best_target[1]

    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        cur = (do - ds, -ds)
        if best_move is None or cur > best_move[0]:
            best_move = (cur, dx, dy)
    return [best_move[1], best_move[2]]