def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    if not resources:
        return [0, 0]

    def clamp_key_for_move(nx, ny):
        # Evaluate move by its best achievable resource advantage.
        # Primary: how much closer the opponent is than we are (opp_d - self_d).
        # Secondary: reduce our distance to that resource; encourage interception near opponent.
        best = None
        for cx, cy in resources:
            self_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            line = abs((ox - nx)) + abs((oy - ny))  # proxy for "approach opponent line"
            key = (opp_d - self_d, -self_d, -line, -cx, -cy)
            if best is None or key > best:
                best = key
        # Penalize stepping onto known obstacles.
        if (nx, ny) in obs:
            best = (-10**9, 0, 0, 0, 0)
        return best

    best_move = [0, 0]
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            key = clamp_key_for_move(nx, ny)
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
    return best_move