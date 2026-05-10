def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in (observation.get("obstacles") or []):
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Prefer the corner farthest from the opponent.
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = None
    # Deterministic tie-breaker order.
    move_order = sorted(moves, key=lambda m: (m[0], m[1]))

    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist_to_opp = cheb(nx, ny, ox, oy)
        dist_to_corner = cheb(nx, ny, far_corner[0], far_corner[1])
        # Also discourage moving too close to any obstacle by preferring fewer adjacent obstacle cells.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    adj_obs += 1

        key = (dist_to_opp, -dist_to_corner, -adj_obs, -abs(nx - sx), -abs(ny - sy))
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]