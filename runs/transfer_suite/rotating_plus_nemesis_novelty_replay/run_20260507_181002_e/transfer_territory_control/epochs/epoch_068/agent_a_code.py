def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    targets = list(unclaimed - obstacles) if unclaimed else []
    if targets:
        tx, ty = min(targets, key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = dist(nx, ny, tx, ty)
        d_to_o = dist(nx, ny, ox, oy)
        score = d_to_t - 0.2 * d_to_o
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best