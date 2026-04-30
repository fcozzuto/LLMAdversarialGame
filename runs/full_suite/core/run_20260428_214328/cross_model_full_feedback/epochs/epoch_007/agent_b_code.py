def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    # If a resource is visible and reachable, move towards closest non-blocked
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
        if not inside(nx, ny) or (nx, ny) in obstacles or (nx, ny) == (ox, oy):
            return [0, 0]
        return [dx, dy]
    # Else move to maximize distance from opponent while staying valid
    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None; best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): continue
        if (nx, ny) in obstacles or (nx, ny) == (ox, oy): 
            continue
        dopp = dist((ox, oy), (nx, ny))
        ds = dist((sx, sy), (nx, ny))
        score = dopp - ds  # prefer moves that increase distance from opponent
        if score > best_score or (score == best_score and (nx, ny) == (sx, sy)):
            best_score = score; best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]
    return [0, 0]