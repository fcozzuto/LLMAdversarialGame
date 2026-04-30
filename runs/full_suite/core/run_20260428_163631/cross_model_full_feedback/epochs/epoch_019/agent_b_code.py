def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    res = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if inb(rx, ry) and (rx, ry) not in obstacles:
            res.append((rx, ry))

    # target factor: weigh toward nearest resource, then toward center, avoiding opponent
    def score_move(dx, dy, nx, ny):
        score = 0
        # nearer to resource is better
        if res:
            nearest = min(res, key=lambda p: cheb(p[0], p[1], nx, ny))
            score -= cheb(nearest[0], nearest[1], nx, ny) * 2
        # stay near center is good to avoid edge traps
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= int(abs(nx - cx) + abs(ny - cy))
        # push away from opponent
        dist_opp = max(1, cheb(nx, ny, ox, oy))
        score += dist_opp
        return score

    best = None
    best_score = None
    for dx, dy, nx, ny in cand:
        sc = score_move(dx, dy, nx, ny)
        if best is None or sc > best_score:
            best = (dx, dy)
            best_score = sc

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]