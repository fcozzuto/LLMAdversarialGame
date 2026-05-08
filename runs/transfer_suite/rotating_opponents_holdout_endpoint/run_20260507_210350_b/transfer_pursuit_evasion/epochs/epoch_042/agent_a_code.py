def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = (observation.get("self_role", "") or "").lower()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1); dy = abs(y2 - y1)
        return dx if dx > dy else dy
    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    is_pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("seeker" in self_role)
    # Opponent action prediction: continues to maximize distance (one step).
    away_dx = 0 if ox == sx else (1 if ox > sx else -1)
    away_dy = 0 if oy == sy else (1 if oy > sy else -1)
    px = clamp(ox + away_dx, 0, w - 1)
    py = clamp(oy + away_dy, 0, h - 1)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_pursuer:
        # Chase predicted position; bias blocking by preferring moves that also reduce distance to the "furthest corner".
        furthest_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        fx, fy = furthest_corner
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d_pred = cheb(nx, ny, px, py)
            d_corner = cheb(nx, ny, fx, fy)
            # Higher is better
            val = (-d_pred * 10) + (-d_corner * 1) + (-(dx == 0 and dy == 0) * 0) + ((dx != 0 or dy != 0) * 0.01)
            key = (val, -abs(nx - ox) - abs(ny - oy))
            if best is None or key > best_val:
                best_val = key
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]
    else:
        # Evader: move to maximize distance from pursuer while steering toward a far corner.
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        tx, ty = target
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            corner_dist = cheb(nx, ny, tx, ty)
            # Higher is better; also prefer progress toward chosen corner.
            key = (d, -corner_dist, -cheb(nx, ny, px, py), (dx == 0 and dy == 0))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]