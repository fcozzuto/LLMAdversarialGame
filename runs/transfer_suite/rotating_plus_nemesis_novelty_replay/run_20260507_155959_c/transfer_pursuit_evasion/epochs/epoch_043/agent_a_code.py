def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        return (nx, ny) if valid(nx, ny) else (x, y)

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("pursur" in self_role) or (self_role == "pursuer")
    my_turn_role_pursuer = is_pursuer

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = None
    if not my_turn_role_pursuer:
        bestd = -1
        for cx, cy in corners:
            d = abs(cx - ox) + abs(cy - oy)
            if d > bestd:
                bestd = d
                target_corner = (cx, cy)

    center = (w // 2, h // 2)
    best_move = (0, 0)
    best_val = None

    for dx, dy in cand:
        nx, ny = step(sx, sy, dx, dy)

        if my_turn_role_pursuer:
            d = cheb((nx, ny), (ox, oy))
            cx, cy = center
            dc = abs(nx - cx) + abs(ny - cy)
            # Prefer smaller distance; tie-break toward staying flexible (lower center bias).
            val = (-d * 1000) - dc
        else:
            # Evader: maximize distance; prefer going to far corner if available; avoid center.
            d = cheb((nx, ny), (ox, oy))
            cx, cy = center
            dc = abs(nx - cx) + abs(ny - cy)
            if target_corner is not None:
                tcx, tcy = target_corner
                toward_corner = abs(ny - tcy) + abs(nx - tcx)
                val = (d * 1000) - toward_corner * 2 + (-dc)
            else:
                val = (d * 1000) - dc

        if best_val is None:
            best_val = val
            best_move = (dx, dy)
        else:
            if my_turn_role_pursuer:
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)
            else:
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]