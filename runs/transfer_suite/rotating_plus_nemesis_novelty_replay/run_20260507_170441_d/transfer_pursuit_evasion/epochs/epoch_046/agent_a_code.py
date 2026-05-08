def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    is_evader = ("evader" in self_role) or ("evader" in opp_role and "pursuer" not in self_role)
    if ("pursuer" in self_role) and ("evader" in opp_role):
        is_evader = False

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev for diagonal pursuit

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist((nx, ny), (ox, oy))
        # Mobility from next state
        mob = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                mob += 1

        # If opponent is cornering, bias to their likely corner (helps pursuer)
        corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
        target_corner = max(corners, key=lambda c: dist((ox, oy), c))
        corner_bias = dist((nx, ny), target_corner) - dist((sx, sy), target_corner)

        # Score: pursuer wants smaller distance; evader wants larger distance
        if is_evader:
            score = (d * 10.0) + (mob * 0.5) + (-corner_bias * 0.8)
        else:
            score = (-d * 10.0) + (mob * 0.4) + (-corner_bias * 0.3)

        if best_score is None or (score > best_score if is_evader else score > best_score):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]