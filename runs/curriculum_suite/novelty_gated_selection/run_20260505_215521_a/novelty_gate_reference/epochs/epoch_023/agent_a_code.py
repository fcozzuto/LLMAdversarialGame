def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(0, 0), (0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if resources:
        best_dir = (0, 0)
        best_score = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = r[0], r[1]
            if not inb(tx, ty):
                continue
            curd = dist((sx, sy), (tx, ty))
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not legal(nx, ny):
                    continue
                nd = dist((nx, ny), (tx, ty))
                sep = dist((nx, ny), (ox, oy))
                score = (curd - nd) * 1000 + sep
                if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_dir):
                    best_score = score
                    best_dir = (dx, dy)
        return [best_dir[0], best_dir[1]]

    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = dist((nx, ny), (ox, oy))
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]