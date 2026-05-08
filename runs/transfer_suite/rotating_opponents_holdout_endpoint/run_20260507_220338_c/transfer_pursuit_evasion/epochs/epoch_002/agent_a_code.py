def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    x0, y0 = int(self_pos[0]), int(self_pos[1])
    xo, yo = int(opp_pos[0]), int(opp_pos[1])

    obstacles = observation.get("obstacles", [])
    ox = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ox.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def wall_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        x, y = x0 + dx, y0 + dy
        if not in_bounds(x, y) or (x, y) in ox:
            continue
        ddx, ddy = x - xo, y - yo
        d2 = ddx * ddx + ddy * ddy
        cheb = max(abs(ddx), abs(ddy))
        wd = wall_dist(x, y)

        if pursuer:
            score = -(10.0 * d2 + 6.0 * cheb + 0.5 * wd)
        else:
            score = 10.0 * d2 + 6.0 * cheb - 0.6 * wd

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx == 0 and dy == 0:
        for ddx, ddy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            x, y = x0 + ddx, y0 + ddy
            if in_bounds(x, y) and (x, y) not in ox:
                dx, dy = ddx, ddy
                break
    return [int(dx), int(dy)]