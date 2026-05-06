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
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_key_from(x, y):
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            d = cheb(x, y, cx, cy)
            return (-d, -d, cx, cy)  # prefer closer to center
        best = None
        best_key = None
        for cx, cy in resources:
            self_d = cheb(x, y, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            key = (opp_d - self_d, -self_d, cx, cy)  # maximize advantage, then closeness, deterministic tie-break
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best_key

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        key = best_key_from(nx, ny)
        if best_val is None or key > best_val:
            best_val = key
            best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_move