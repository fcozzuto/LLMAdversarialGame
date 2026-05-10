def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    ax, ay = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ax, ay, ox, oy = int(ax), int(ay), int(ox), int(oy)

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    oppT = toset(observation.get("opponent_territory"))

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda t: (dist(ax, ay, t[0], t[1]), t[1], t[0]))
    else:
        candidates = oppT if oppT else {(ox, oy)}
        tx, ty = min(candidates, key=lambda t: (dist(ax, ay, t[0], t[1]), t[1], t[0]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestd = None
    bestm = (0, 0)

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist(nx, ny, tx, ty)
        if bestd is None or d < bestd or (d == bestd and (dy, dx) < (bestm[1], bestm[0])):
            bestd, bestm = d, (dx, dy)

    return [int(bestm[0]), int(bestm[1])]