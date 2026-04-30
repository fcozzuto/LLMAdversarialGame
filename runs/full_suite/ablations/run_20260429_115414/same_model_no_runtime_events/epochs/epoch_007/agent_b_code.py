def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for p in (observation.get("resources", []) or []):
        if p is not None and len(p) >= 2:
            resources.append((p[0], p[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if resources:
            dres = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < dres: dres = d
            score += 2000 if (nx, ny) in set(resources) else 0
            score += -dres
        d_op = cheb(nx, ny, ox, oy)
        score += -2 * d_op
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]