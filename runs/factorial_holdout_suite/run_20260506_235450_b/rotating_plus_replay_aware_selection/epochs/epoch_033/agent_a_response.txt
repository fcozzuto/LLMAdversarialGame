def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Prefer moves that improve our "race margin" on the most contestable nearby resource.
    # Margin = opp_dist - self_dist (higher means we get there first).
    # Add a small bias to closer targets to reduce dithering.
    def cell_value(nx, ny):
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds
            # Safety: if opponent is closer (margin < 0), penalize heavily.
            # Otherwise favor larger margin, then smaller ds, then deterministic preference by (rx,ry).
            val = (margin, -ds, -rx, -ry)
            if best is None or val > best[0]:
                best = (val, (rx, ry))
        return best[0]

    best_move = None
    best_val = None
    # Deterministic tie-break: fixed dir order already, plus lexicographic on move.
    for dx, dy, nx, ny in legal:
        v = cell_value(nx, ny)
        if best_val is None or v > best_val or (v == best_val and (dx, dy) > best_move):
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]