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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dist_to_nearest_obstacle(x, y):
        if not obstacles:
            return 99
        best = 0
        for bx, by in obstacles:
            d = cheb(x, y, bx, by)
            if d > best:
                best = d
        return best

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)
        d_obs = dist_to_nearest_obstacle(nx, ny)
        d_ctr = -cheb(nx, ny, int(cx), int(cy))  # closer to center => larger

        if is_evader:
            val = (d_op, d_obs, d_ctr, -cheb(nx, ny, 0, 0), -cheb(nx, ny, w - 1, h - 1))
        else:
            val = (-d_op, d_obs, d_ctr, cheb(nx, ny, 0, 0), cheb(nx, ny, w - 1, h - 1))

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move