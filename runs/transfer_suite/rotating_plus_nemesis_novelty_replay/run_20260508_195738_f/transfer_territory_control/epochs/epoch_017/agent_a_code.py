def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in ox if p and len(p) >= 2}
    opp = observation.get("opponent_position", None) or [None, None]
    oppx, oppy = (opp[0], opp[1]) if len(opp) >= 2 else (None, None)

    res = observation.get("resources", []) or []
    resources = [(p[0], p[1]) for p in res if p and len(p) >= 2]
    cx, cy = w // 2, h // 2

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def nearest_resource_dist(nx, ny):
        if not resources:
            return man(nx, ny, cx, cy)
        m = 10**9
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if d < m:
                m = d
        return m

    def opp_dist(nx, ny):
        if oppx is None or oppy is None:
            return 0
        return man(nx, ny, oppx, oppy)

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            score = -10**12
        else:
            dr = nearest_resource_dist(nx, ny)
            do = opp_dist(nx, ny)
            score = (do * 5) - (dr * 2) - (1 if (dx == 0 and dy == 0) else 0)
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]