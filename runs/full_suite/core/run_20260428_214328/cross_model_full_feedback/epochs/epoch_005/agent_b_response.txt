def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    # 1) If a closest resource accessible, move toward it
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
    # 2) Otherwise move to maximize distance from opponent
    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None; best_score = -9999
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): continue
        if (nx, ny) in obstacles: continue
        if (nx, ny) == (ox, oy): continue
        dop = dist((nx, ny), (ox, oy))
        ds = dist((sx, sy), (ox, oy))
        score = dop - ds
        if score > best_score or (score == best_score and ((nx, ny) < best)):
            best_score = score; best = (nx, ny)
    if best is not None:
        nx, ny = best
        return [nx - sx, ny - sy]
    # 3) Fallback: stay or move away if possible
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != (ox, oy):
            return [dx, dy]
    return [0, 0]