def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if resources:
        tx, ty = min(resources, key=lambda p: md(mx, my, p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not inb(nx, ny):
            continue
        d = md(nx, ny, tx, ty)
        # deterministic tiebreak: prefer smaller dx/dy order via tuple
        cand = (d, md(nx, ny, ox, oy), dx, dy)
        if cand < best:
            best = cand

    return [int(best[2]), int(best[3])]