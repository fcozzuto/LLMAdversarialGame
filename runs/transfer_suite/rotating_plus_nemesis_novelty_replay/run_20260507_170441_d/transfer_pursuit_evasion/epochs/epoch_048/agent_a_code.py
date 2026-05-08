def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("pursuer" in self_role) and ("evader" not in self_role)
    if ("pursuer" in opp_role) and ("evader" in self_role):
        self_is_pursuer = False

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
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
            if free(nx, ny):
                c += 1
        return c

    # Prefer corners for evasion; chase using Chebyshev distance for pursuit.
    corner_targets = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = max(corner_targets, key=lambda t: cheb(t[0], t[1], sx, sy))

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        open_ct = open_neighbors(nx, ny)

        if self_is_pursuer:
            # Small bias toward mobility and toward corner "pressure" (avoid running into obstacles).
            score = -dist * 1000 + open_ct
            tie_target = cheb(nx, ny, corner[0], corner[1])
        else:
            # Evade: maximize distance to opponent; if equal, head toward farthest corner; avoid dead-ends.
            score = dist * 1000 + open_ct
            tie_target = cheb(nx, ny, corner[0], corner[1])

        key = (score, tie_target, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]