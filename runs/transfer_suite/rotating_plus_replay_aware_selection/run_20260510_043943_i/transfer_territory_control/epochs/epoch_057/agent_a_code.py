def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    moves = [(0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)]
    best = None
    bestv = None

    def md(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if res:
            dmin = None
            for rx, ry in res:
                d = md(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
            score = (dmin, md(nx, ny, ox, oy))
        else:
            score = (0, -md(nx, ny, ox, oy))
        if bestv is None or score < bestv:
            bestv = score
            best = [dx, dy]

    return best if best is not None else [0, 0]