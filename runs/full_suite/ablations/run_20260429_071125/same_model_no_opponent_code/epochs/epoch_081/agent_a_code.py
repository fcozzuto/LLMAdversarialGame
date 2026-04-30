def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w or 8)
    except:
        w = 8
    try:
        h = int(h or 8)
    except:
        h = 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def manhattan(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    tx, ty = resources[0]
    bestd = manhattan(sx, sy, tx, ty)
    for x, y in resources[1:]:
        d = manhattan(sx, sy, x, y)
        if d < bestd:
            bestd, tx, ty = d, x, y

    moves = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)]
    best = None
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = manhattan(nx, ny, tx, ty)
        if (nx, ny) == (ox, oy):
            score += 2
        if best is None or score < bestscore:
            best, bestscore = [dx, dy], score
    if best is None:
        return [0, 0]
    return best