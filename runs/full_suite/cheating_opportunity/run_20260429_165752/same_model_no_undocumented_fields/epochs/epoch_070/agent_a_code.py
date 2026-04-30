def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    if not free(sx, sy):
        for dx, dy in dirs:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                res.append((x, y))

    if res:
        tx, ty = min(res, key=lambda r: cheb(sx, sy, r[0], r[1]))
    else:
        tx, ty = w // 2, h // 2

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dres = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)
        curdop = cheb(sx, sy, ox, oy)
        # If opponent is close, prefer moves that increase distance from them.
        opp_bonus = (1 if curdop <= 2 else 0) * (-dop)
        score = (dres, opp_bonus, dx, dy)
        if best is None or score < best:
            best = score
            best_move = [dx, dy]
    return best_move if best is not None else [0, 0]