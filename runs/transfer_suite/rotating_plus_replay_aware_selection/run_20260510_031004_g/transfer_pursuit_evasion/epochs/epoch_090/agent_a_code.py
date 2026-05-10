def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("evad" not in self_role and "purs" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def obst_near(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    c += 1
        return c

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for nx, ny, dx, dy in candidates:
        d = cheb(nx, ny)
        near = obst_near(nx, ny)
        # Pursuer: minimize distance, prefer moving into open space.
        # Evader: maximize distance, prefer using obstacles (higher near), and avoid hugging center too hard.
        if self_is_pursuer:
            score = (-d * 10.0) - near * 0.6 + (abs(nx - cx) + abs(ny - cy)) * 0.05
        else:
            score = (d * 10.0) + near * 0.8 - (abs(nx - cx) + abs(ny - cy)) * 0.02
        # Deterministic tie-breaker: prefer smaller dx/dy lexicographically and then lower distance variance
        tie = (0 if dx == 0 else 1, 0 if dy == 0 else 1, d, nx, ny)
        key = (score, -tie[2], -tie[3], -tie[4])
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    return best[1]