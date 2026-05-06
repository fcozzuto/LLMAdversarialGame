def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    res = [tuple(p) for p in resources]
    obs = set(tuple(p) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to_res = None
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            d = cheb(nx, ny, rx, ry)
            if d_to_res is None or d < d_to_res:
                d_to_res = d
        if d_to_res is None:
            d_to_res = 999999

        d_to_opp = cheb(nx, ny, ox, oy)
        score = -d_to_res + (2 if d_to_opp <= 1 else 0) - 0.2 * d_to_opp
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move