def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b, c, d):
        a, b, c, d = int(a), int(b), int(c), int(d)
        return max(abs(a - c), abs(b - d))

    if res:
        tx, ty = min(res, key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = w // 2, h // 2

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_t = dist(nx, ny, tx, ty)
        d_o = dist(nx, ny, ox, oy)
        cand = (d_t, -d_o, dx, dy)
        if best is None or cand < best[0]:
            best = (cand, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]