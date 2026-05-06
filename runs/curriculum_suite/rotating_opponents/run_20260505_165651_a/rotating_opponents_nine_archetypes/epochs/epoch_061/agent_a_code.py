def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def score_cell(x, y):
        if blocked(x, y): return None
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return (man(x, y, cx, cy) + 0.2 * man(x, y, ox, oy), 0)
        best = None
        for rx, ry in resources:
            ds = man(x, y, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where we are not behind, but still progress
            # Tie-break by favoring nearer to us and farther from opponent
            key = (max(ds - do, -20), ds, -do, -((rx + ry) & 1))
            if best is None or key < best:
                best = key
        # Avoid being too close to opponent unless we have a clear target advantage
        risk = man(x, y, ox, oy)
        adv = resources and best and (best[0] <= -1)
        penalty = 0 if adv else (0.35 * max(0, 3 - risk))
        return (best[0] + penalty, best[1])

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        k = score_cell(nx, ny)
        if k is None:
            continue
        # Deterministic tie-break: prefer moves with smaller (dx,dy) lexicographically
        key = (k[0], k[1], dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move