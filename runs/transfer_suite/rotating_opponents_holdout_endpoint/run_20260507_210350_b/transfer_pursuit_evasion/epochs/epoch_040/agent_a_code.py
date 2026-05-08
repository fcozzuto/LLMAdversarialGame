def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = (observation.get("self_role", "") or "").lower()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx if dx > dy else dy

    def clamp_dir(a, b):
        if a == b:
            return 0
        return 1 if b > a else -1

    # Role-based policy: pursuer chases, evader runs.
    is_pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("seeker" in self_role)
    if is_pursuer:
        best = None
        best_key = None
        for dx, dy in moves:
            nsx, nsy = sx + dx, sy + dy
            if not valid(nsx, nsy):
                continue
            dist = cheb(nsx, nsy, ox, oy)
            key = (-dist, dx == 0 and dy == 0)  # prefer moving
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]
    else:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        # Choose a far corner relative to opponent
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        # Score moves by distance increase primarily, tie-break by steering toward chosen target
        best = None
        best_key = None
        for dx, dy in moves:
            nsx, nsy = sx + dx, sy + dy
            if not valid(nsx, nsy):
                continue
            dist = cheb(nsx, nsy, ox, oy)
            steer = -cheb(nsx, nsy, tx, ty)
            # Prefer larger distance; if tie, prefer steering; if still tie, prefer not staying still
            key = (dist, steer, dx == 0 and dy == 0)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        if best is None:
            return [0, 0]
        # If all moves worsen distance, stay (deterministic), else take best.
        cur_dist = cheb(sx, sy, ox, oy)
        if cheb(sx + best[0], sy + best[1], ox, oy) < cur_dist and any(valid(sx + dx, sy + dy) for dx, dy in moves):
            return [0, 0]
        return [best[0], best[1]]