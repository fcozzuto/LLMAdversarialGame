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
    self_is_evader = ("evader" in self_role) or ("evader" in opp_role and "pursuer" not in self_role)
    is_pursuer = not self_is_evader

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_corner_dist(x, y):
        bc = -1
        for cx, cy in corners:
            d = cheb(x, y, cx, cy)
            if d > bc:
                bc = d
        return bc

    # If evader: maximize distance to pursuer and prefer moving toward safer corners.
    # If pursuer: minimize distance to evader while avoiding obstacles.
    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        corner_d = best_corner_dist(nx, ny)
        # local obstacle avoidance: prefer positions with more free neighbors
        free_n = 0
        for ex, ey in dirs:
            tx, ty = nx + ex, ny + ey
            if valid(tx, ty):
                free_n += 1
        if is_pursuer:
            score = (-d * 10) + (free_n * 0.2) + (corner_d * 0.02)
        else:
            score = (d * 10) + (corner_d * 0.3) + (free_n * 0.1)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move