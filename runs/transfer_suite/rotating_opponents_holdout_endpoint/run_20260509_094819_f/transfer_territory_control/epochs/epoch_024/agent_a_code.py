def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def to_set(v):
        if not v:
            return set()
        it = v.keys() if isinstance(v, dict) else v
        out = set()
        for p in it:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.add((int(p[0]), int(p[1])))
        return out

    obstacles = to_set(observation.get("obstacles") or [])
    resources = to_set(observation.get("resources") or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target = None
    if resources:
        bestd = 10**18
        for (rx, ry) in resources:
            if (rx, ry) in obstacles:
                continue
            d = dist(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                target = (rx, ry)

    best_score = 10**18
    best_move = [0, 0]
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if target is not None:
            score = dist(nx, ny, target[0], target[1])
        else:
            score = dist(nx, ny, w // 2, h // 2)
        score += 0.25 * dist(nx, ny, ox, oy)  # mild avoidance of opponent
        if score < best_score:
            best_score = score
            best_move = [int(dx), int(dy)]
    return best_move