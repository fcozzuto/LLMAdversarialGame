def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Avoid obstacles and opponent cell
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): 
            continue
        if (nx, ny) in obstacles: 
            continue
        if (nx, ny) == (ox, oy):
            continue
        candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Target closest resource if reachable; else head toward opponent to contest
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best_r = None; best_d = 10**9
    for r in resources:
        rx, ry = r[0], r[1]
        if not inside(rx, ry) or (rx, ry) in obstacles:
            continue
        d = dist((sx, sy), (rx, ry))
        if d < best_d:
            best_d = d; best_r = (rx, ry)
    if best_r is not None:
        rx, ry = best_r
        dx = 1 if rx > sx else -1 if rx < sx else 0
        dy = 1 if ry > sy else -1 if ry < sy else 0
        nx, ny = sx + dx, sy + dy
        if (dx, dy, nx, ny) in [(a,b,c,d) for (a,b,c,d) in candidates]:
            return [dx, dy]

    # Otherwise move toward opponent to challenge, using simple rule
    dx = 1 if ox > sx else -1 if ox < sx else 0
    dy = 1 if oy > sy else -1 if oy < sy else 0
    nx, ny = sx + dx, sy + dy
    if (dx, dy, nx, ny) in [(a,b,c,d) for (a,b,c,d) in candidates]:
        return [dx, dy]

    # Fallback to any safe move that does not collide
    return [candidates[0][0], candidates[0][1]]