def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obs
    def dist(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy  # Chebyshev for 8-dir movement
    def score(nx, ny):
        if not res:
            return dist(nx, ny, ox, oy) - 0.1 * (nx*nx + ny*ny)
        best = None
        bo = dist(nx, ny, ox, oy)
        for rx, ry in res:
            myd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            v = (od - myd) * 1000 - myd
            if best is None or (v, -bo, rx, ry) > best:
                best = (v, -bo, rx, ry)
        return best[0] if best else 0

    best_move = None; best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny): 
            continue
        v = score(nx, ny)
        key = (v, dist(nx, ny, ox, oy), dx, dy, nx, ny)
        if best_val is None or key > best_val:
            best_val = key; best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]