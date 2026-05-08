def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_move = (0, 0)

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_corner = None
        best_corner_val = -1
        for cx, cy in corners:
            v = cheb(cx, cy, ox, oy)
            if v > best_corner_val:
                best_corner_val = v
                best_corner = (cx, cy)
        tx, ty = best_corner

        # Greedy: move toward chosen far corner while also increasing distance from pursuer.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            v_corner = -cheb(nx, ny, tx, ty)
            v_dist = cheb(nx, ny, ox, oy)
            val = (v_dist * 1000) + v_corner
            if best is None or val > best:
                best = val
                best_move = (dx, dy)
    else:
        # Greedy pursuer: minimize distance; block-adjacent squares get a slight penalty.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            adj_pen = 0
            for ax, ay in obstacles:
                if cheb(nx, ny, ax, ay) <= 1 and (nx, ny) != (ax, ay):
                    adj_pen = 1
                    break
            val = -(dist * 1000) - adj_pen
            if best is None or val > best:
                best = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]