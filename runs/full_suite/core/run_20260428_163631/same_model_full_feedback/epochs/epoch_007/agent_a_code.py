def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res.append((r[0], r[1]))
    if not res:
        # No resources known: move toward opponent to pressure, else hold.
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
        best = None
        bestv = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if safe(nx, ny):
                v = cd(nx, ny, ox, oy)
                if best is None or v < bestv:
                    best = (dx, dy)
                    bestv = v
        return [best[0], best[1]] if best is not None else [0, 0]

    deltas = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        myd = min(cd(nx, ny, rx, ry) for rx, ry in res)
        opd = min(cd(ox, oy, rx, ry) for rx, ry in res)
        # Prefer moves that reduce our distance more than the opponent's.
        score = (opd - myd, -myd, -cd(nx, ny, ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]