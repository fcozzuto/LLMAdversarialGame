def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(observation.get("obstacles", []) or [])
    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    role = str(observation.get("self_role", "") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        d = cheb(nx, ny, ox, oy)
        val = d if not pursuer else -d
        if best_val is None:
            best_val = val
            best = (dx, dy)
        else:
            if val > best_val:
                best_val = val
                best = (dx, dy)
    return [int(best[0]), int(best[1])]