def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    rset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                rset.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)
    minimize = is_pursuer

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    best_move = moves[4]
    best_dist = cheb(sx, sy, ox, oy)
    best_t = 0

    for idx, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in rset:
            nx, ny = sx, sy
        d = cheb(nx, ny, ox, oy)
        better = (d < best_dist) if minimize else (d > best_dist)
        tie = d == best_dist
        if better or (tie and idx < best_t):
            best_dist = d
            best_move = [dx, dy]
            best_t = idx

    return best_move