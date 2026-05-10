def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def nearest_corner(px, py):
        best = corners[0]
        bd = cheb(px, py, best[0], best[1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if d < bd:
                bd = d
                best = (cx, cy)
        return best

    def farthest_corner(px, py):
        best = corners[0]
        bd = cheb(px, py, best[0], best[1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if d > bd:
                bd = d
                best = (cx, cy)
        return best

    opp_target_corner = nearest_corner(ox, oy)
    self_escape_corner = farthest_corner(ox, oy)

    best = None
    if pursuer:
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            dist_to_corner = cheb(nx, ny, opp_target_corner[0], opp_target_corner[1])
            # primary: minimize distance to opponent; secondary: push toward opponent's nearest corner
            key = (d, dist_to_corner, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
    else:
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            dist_from_corner = cheb(nx, ny, self_escape_corner[0], self_escape_corner[1])
            # primary: maximize distance from pursuer; secondary: head toward farthest corner from pursuer
            key = (-d, -dist_from_corner, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]