def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def d(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    if res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            for rx, ry in res:
                if nx == rx and ny == ry:
                    return [dx, dy]

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if res:
            mind = min(d(nx, ny, rx, ry) for rx, ry in res)
        else:
            mind = 0
        od = d(nx, ny, ox, oy)
        score = (-(mind * 10)) + od
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]