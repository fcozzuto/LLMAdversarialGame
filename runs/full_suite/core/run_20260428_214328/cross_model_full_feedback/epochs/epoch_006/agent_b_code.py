def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Priority 1: move toward closest accessible resource not blocked
    best_r = None; best_d = 10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles or (rx, ry) == (ox, oy):
            continue
        d = dist((sx, sy), (rx, ry))
        if d < best_d:
            best_d = d; best_r = (rx, ry)
    if best_r is not None:
        rx, ry = best_r
        dx = 1 if rx > sx else -1 if rx < sx else 0
        dy = 1 if ry > sy else -1 if ry < sy else 0
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles or (nx, ny) == (ox, oy):
            return [0, 0]
        return [dx, dy]

    # Priority 2: stay close to not get cornered: move to maximize distance from opponent
    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None; best_score = -9999
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): continue
        if (nx, ny) in obstacles: continue
        # score by distance to opponent and centrality
        od = dist((nx, ny), (ox, oy))
        center = abs(nx - (w-1)/2) + abs(ny - (h-1)/2)
        score = od + (-center)
        if score > best_score:
            best_score = score; best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]
    # Fallback: stay
    return [0, 0]