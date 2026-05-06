def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    if not resources:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # For this candidate, pick the best resource for us relative to opponent
        val = None
        for cx, cy in resources:
            self_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            key = (opp_d - self_d, -self_d, -cx, -cy)
            if val is None or key > val:
                val = key
        if val is None:
            continue

        # small preference to reduce distance to opponent if tied (more interference potential)
        opp_close = -cheb(nx, ny, ox, oy)
        full = (val, opp_close)
        if best_val is None or full > best_val:
            best_val = full
            best_move = [dx, dy]

    return best_move