def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("pursue" in role)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dist_to_nearest_corner(x, y):
        dmin = 10**9
        for cx, cy in corners:
            d = abs(x - cx) + abs(y - cy)
            if d < dmin: dmin = d
        return dmin

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            score = -10**7
        else:
            d_op = cheb(nx, ny, ox, oy)
            corner_bias = dist_to_nearest_corner(nx, ny) - dist_to_nearest_corner(ox, oy)
            # If pursuer: prefer smaller distance to opponent and smaller distance-to-corner advantage.
            # If evader: prefer larger distance and larger distance-to-corner advantage.
            obstacle_near = 0
            for ax, ay in obs:
                md = abs(nx - ax) + abs(ny - ay)
                if md == 0:
                    obstacle_near = 50
                    break
                if md < 3:
                    obstacle_near = max(obstacle_near, 6 - md)
            if pursuer:
                score = (-1000 * d_op) + (-6 * corner_bias) + (-12 * obstacle_near)
            else:
                score = (1000 * d_op) + (6 * corner_bias) + (-12 * obstacle_near)
        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]