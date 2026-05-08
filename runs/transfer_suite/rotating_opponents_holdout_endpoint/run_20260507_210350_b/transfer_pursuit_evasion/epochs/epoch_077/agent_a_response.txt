def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    role_opp = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = any(k in role_self for k in ("pursuer", "chaser", "hunter"))
    opp_is_pursuer = any(k in role_opp for k in ("pursuer", "chaser", "hunter"))
    am_pursuer = self_is_pursuer if (self_is_pursuer or opp_is_pursuer) else True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corners = [c for c in corners if not blocked(c[0], c[1])] or corners

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        if am_pursuer:
            d = cd(nx, ny, ox, oy)
            # tie-break: lexicographically minimize (x,y) deltas toward opponent
            tx = nx - ox
            if tx < 0:
                tx = -tx
            ty = ny - oy
            if ty < 0:
                ty = -ty
            val = (d, tx + ty, nx, ny)
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)
        else:
            # evader: maximize distance from pursuer while steering to farthest free corner
            d_away = cd(nx, ny, ox, oy)
            # choose target corner deterministically from current positions
            tc = None
            best_corner_dist = None
            for cx, cy in corners:
                dist_corner = cd(ox, oy, cx, cy)
                if best_corner_dist is None or dist_corner > best_corner_dist:
                    best_corner_dist = dist_corner
                    tc = (cx, cy)
            cx, cy = tc
            d_to_corner = cd(nx, ny, cx, cy)
            val = (-d_away, d_to_corner, nx, ny)
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]