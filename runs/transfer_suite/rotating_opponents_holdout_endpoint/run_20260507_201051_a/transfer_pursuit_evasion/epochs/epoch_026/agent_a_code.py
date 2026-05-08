def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("chase" in role) or ("pursuer" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_adj(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in obs:
                    c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    fx, fy = far_corner

    best_move = (0, 0)
    best_key = None
    # key: tuple comparable; for pursuer maximize, for evader maximize
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        dist_to_op = cheb(nx, ny, ox, oy)
        a = obs_adj(nx, ny)
        # wall runner preference: keep near an edge (evader) or use edges to trap (pursuer)
        wall = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)
        # corner pressure/escape
        corner_dist = cheb(nx, ny, fx, fy)
        center = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)

        if is_pursuer:
            key = (-(dist_to_op), -a, wall, -corner_dist, -center, dx, dy)
        else:
            key = (dist_to_op, a, wall, -corner_dist, center, -dx, -dy)

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]