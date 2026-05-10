def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or (("evader" in opp_role) and ("pursuer" not in self_role))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = None
    best_corner_val = -1
    for cx, cy in corners:
        d = abs(cx - ox) + abs(cy - oy)
        if d > best_corner_val:
            best_corner_val = d
            far_corner = (cx, cy)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_obst(x, y):
        if not obstacles:
            return 99
        best = 99
        for bx, by in obstacles:
            d = cheb(x, y, bx, by)
            if d < best:
                best = d
        return best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_move():
        best_score = None
        best = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            d_opp = cheb(nx, ny, ox, oy)
            d_corner = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
            d_obst = nearest_obst(nx, ny)
            obst_pen = 0.0 if d_obst >= 3 else (3 - d_obst) * 0.8

            if is_evader:
                score = (d_opp * 2.0) + (d_corner * 0.15) - obst_pen
            else:
                # pursuer: reduce distance strongly; prefer moves that also keep away from obstacles
                score = (-d_opp * 2.5) + (-abs(nx - ox) - abs(ny - oy)) * 0.08 - obst_pen

            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    return best_move()