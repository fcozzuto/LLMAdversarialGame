def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    self_role = str(observation.get("self_role", "")).lower()
    self_is_pursuer = ("purs" in self_role) or ("catch" in self_role) or ("tag" in self_role)

    def blocked(x, y):
        return any(bx == x and by == y for bx, by in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Deterministic "zigzag" prediction using last seen displacement if available
    # (If no history, fall back to aiming directly.)
    px, py = ox, oy
    if "opponent_path" in observation and observation.get("opponent_path") is not None:
        path = observation.get("opponent_path", [])
        if isinstance(path, list) and len(path) >= 2 and all(isinstance(p, list) for p in path[-2:]):
            (ax, ay), (bx, by) = path[-2], path[-1]
            px, py = bx + (bx - ax), by + (by - ay)
    if not in_bounds(px, py):
        px, py = ox, oy

    steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_score = None

    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue

        # Distance/capture evaluation
        adx, ady = ox - nx, oy - ny
        dist2 = adx * adx + ady * ady
        pdx, pdy = px - nx, py - ny
        pred2 = pdx * pdx + pdy * pdy

        # Obstacle avoidance: discourage stepping near obstacles
        near_obs = 0
        for bx, by in obstacles:
            ddx, ddy = nx - bx, ny - by
            near_obs += 1 if ddx * ddx + ddy * ddy <= 1 else 0

        # Corner/edge behavior
        edge_dist = min(nx, ny, (w - 1) - nx, (h - 1) - ny)

        # If pursuer: minimize predicted distance; also prefer not to get stuck near obstacles.
        if self_is_pursuer:
            score = pred2 * 10 + dist2 + near_obs * 50 - edge_dist * 0.5
            better = (best_score is None) or (score < best_score)
        else:
            # If evader: maximize predicted distance; prefer larger edge_dist (stay away from walls) if safe.
            score = -(pred2 * 10 + dist2) - near_obs * 30 + edge_dist * 0.8
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best = [dx, dy]

    return best