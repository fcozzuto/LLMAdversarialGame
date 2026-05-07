def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, dict):
            x = p.get("x", None); y = p.get("y", None)
            if x is not None and y is not None:
                obstacles.add((int(x), int(y)))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, dict):
            x = r.get("x", None); y = r.get("y", None)
            if x is not None and y is not None:
                res.append((int(x), int(y)))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if res:
            dmin = 10**9
            for rx, ry in res:
                d = md(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
        else:
            # deterministic drift to one corner when no resources
            dmin = md(nx, ny, 0 if sx > (w - 1) // 2 else (w - 1), h - 1 if sy < h // 2 else 0)
        oppd = md(nx, ny, ox, oy)
        score = (dmin, -oppd, dx, dy)
        if best is None or score < best[0]:
            best = (score, [dx, dy])
    return best[1] if best is not None else [0, 0]