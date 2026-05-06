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

    def resource_value(px, py):
        if not resources:
            return 0
        best = None
        for cx, cy in resources:
            self_d = cheb(px, py, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            key = (opp_d - self_d, -self_d, -cx, -cy)
            if best is None or key > best:
                best = key
        return best[0] * 100 - best[1]  # emphasize getting nearer while beating opponent

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        hit = (nx, ny) in obs
        val = resource_value(nx, ny)
        if hit:
            val -= 10_000
        # tie-break: prefer moves that change position if score equal, then deterministic order
        tie = (val, 0 if (dx == 0 and dy == 0) else 1, -dx, -dy)
        if best_score is None or tie > best_score:
            best_score = tie
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]