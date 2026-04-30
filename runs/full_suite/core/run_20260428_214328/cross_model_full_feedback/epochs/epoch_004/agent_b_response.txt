def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    # Basic deterministic heuristic:
    # 1) If a resource exists, move toward the closest resource not blocked by obstacle/opponent.
    # 2) If no resource accessible, move to maximize distance from opponent (greedy).
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    best_r = None; best_d = 10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = dist((sx, sy), (rx, ry))
        if d < best_d:
            best_d = d; best_r = (rx, ry)
    if best_r is not None:
        rx, ry = best_r
        dx = 1 if rx > sx else -1 if rx < sx else 0
        dy = 1 if ry > sy else -1 if ry < sy else 0
        nx, ny = sx + dx, sy + dy
        if (nx, ny) == (ox, oy) or not inside(nx, ny) or (nx, ny) in obstacles:
            return [0, 0]
        return [dx, dy]
    # No accessible resource; move to keep some distance from opponent
    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None; best_score = -9999
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # score: prefer increasing distance to opponent; tiebreaker prefer smaller move
        d_to_opp = dist((nx, ny), (ox, oy))
        score = d_to_opp
        if score > best_score:
            best_score = score; best = (ddx, ddy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]