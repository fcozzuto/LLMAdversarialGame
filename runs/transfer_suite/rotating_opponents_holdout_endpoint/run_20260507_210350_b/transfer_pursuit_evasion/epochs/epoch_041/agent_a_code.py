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

    is_pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("seeker" in self_role)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    best_move = (0, 0)
    if is_pursuer:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            key = (-dist, 0 if (dx == 0 and dy == 0) else 1, -((dx != 0) and (dy != 0)))
            # maximizing key -> prefer smaller dist because -dist larger is better? invert:
            key = (-(dist), 0 if (dx == 0 and dy == 0) else 1, -((dx != 0) and (dy != 0)))
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        # Evader: run away and bias toward the farthest corner.
        target_corner = None
        best_corner_score = None
        for cx, cy in corners:
            score = cheb(sx, sy, cx, cy)
            if best_corner_score is None or score > best_corner_score:
                best_corner_score = score
                target_corner = (cx, cy)

        tx, ty = target_corner
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_away = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, tx, ty)
            # maximize: farther from pursuer, also farther toward chosen corner; prefer diagonal, avoid staying.
            key = (d_away, d_corner, -((dx == 0 and dy == 0)), -((dx == 0) ^ (dy == 0)))
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]