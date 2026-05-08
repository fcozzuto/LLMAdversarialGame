def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None:
            obstacles.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("catch" in role) or ("purs" in opp_role) or ("catch" in opp_role)

    # Deterministic direction order (center first when tie-breaking)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance
        if is_pursuer:
            score = -dist
            # prefer moving to center when distances tie
            score -= 0.001 * (abs(nx - cx) + abs(ny - cy))
        else:
            score = dist
            # avoid drifting toward opponent corner if we can
            own_corner = (0, 0) if (sx <= (w - 1) / 2.0 and sy <= (h - 1) / 2.0) else (w - 1, h - 1)
            opp_corner = (0, h - 1) if own_corner == (w - 1, h - 1) else (w - 1, 0)
            score -= 0.001 * (cheb(nx, ny, *opp_corner))
            # also prefer center slightly to keep options
            score -= 0.0005 * (abs(nx - cx) + abs(ny - cy))

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]