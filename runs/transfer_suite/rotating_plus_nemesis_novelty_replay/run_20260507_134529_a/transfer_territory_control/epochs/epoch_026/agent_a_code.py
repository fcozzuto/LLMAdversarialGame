def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w)
    except:
        w = 8
    try:
        h = int(h)
    except:
        h = 8

    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = [(dx, dy, sx + dx, sy + dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not candidates:
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    def d2(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    best = None
    for dx, dy, nx, ny in candidates:
        score = 0
        if (nx, ny) in opp_terr:
            score += 5000
        if resources:
            score += 3000 - 3 * min(d2(nx, ny, rx, ry) for rx, ry in resources)
        else:
            score += 1000 - d2(nx, ny, ox, oy)
        score -= 10 * (abs(nx - ox) + abs(ny - oy))
        score -= 1 if (nx == sx and ny == sy) else 0
        key = (score, -abs(dx), -abs(dy), -nx, -ny)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]