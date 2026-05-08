def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("pursuer" in self_role) and ("evader" not in self_role)
    if ("pursuer" in opp_role) and ("evader" in self_role):
        self_is_pursuer = False

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def open_neighbors(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if free(nx, ny): c += 1
        return c

    if self_is_pursuer:
        # Intercept: minimize Chebyshev distance; tie-break by more mobility; deterministic order.
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): continue
            d = cheb(nx, ny, ox, oy)
            score = (d, -open_neighbors(nx, ny), dx, dy)
            if best is None or score < best[0]:
                best = (score, [dx, dy])
        return best[1] if best is not None else [0, 0]
    else:
        # Evade: run to farthest corner while respecting obstacles and keeping distance.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), c[0], c[1]))
        tx, ty = target
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): continue
            d = cheb(nx, ny, ox, oy)
            # Prefer moving toward chosen target when distances are equal.
            toward = cheb(nx, ny, tx, ty)
            score = (-d, toward, dx, dy)
            if best is None or score < best[0]:
                best = (score, [dx, dy])
        return best[1] if best is not None else [0, 0]