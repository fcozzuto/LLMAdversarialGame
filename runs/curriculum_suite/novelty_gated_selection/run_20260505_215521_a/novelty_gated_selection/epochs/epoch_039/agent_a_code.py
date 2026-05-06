def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        t = a - c
        if t < 0:
            t = -t
        u = b - d
        if u < 0:
            u = -u
        return t + u

    def min_dist_to_resources(x, y):
        if not res:
            return 999999
        m = None
        for rx, ry in res:
            d = md(x, y, rx, ry)
            if m is None or d < m:
                m = d
        return m if m is not None else 999999

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        dres = min_dist_to_resources(nx, ny)
        dop = md(nx, ny, ox, oy)
        score = -dres * 10 + dop
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    nx0, ny0 = sx, sy
    if inb(nx0, ny0) and (nx0, ny0) not in obst:
        return [0, 0]
    return best_move