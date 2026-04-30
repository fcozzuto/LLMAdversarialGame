def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = [(dx, dy) for dx, dy in deltas if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    me = (sx, sy)
    opp = (ox, oy)

    if resources:
        nearest = min(resources, key=lambda r: dist((sx, sy), r))
        tx, ty = nearest
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        cand = (dx, dy)
        if cand in legal:
            return [dx, dy]
        # try alternative towards resource if direct blocked
        for d in legal:
            nx, ny = sx + d[0], sy + d[1]
            if dist((nx, ny), (tx, ty)) < dist((sx, sy), (tx, ty)):
                return [d[0], d[1]]

    # Fallback: move toward closest to opponent to limit escape
    best = None
    best_score = None
    for d in legal:
        nx, ny = sx + d[0], sy + d[1]
        od = dist((nx, ny), opp)
        score = -od
        if best is None or score > best_score:
            best = d
            best_score = score
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]