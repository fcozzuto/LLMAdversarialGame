def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    # If there is a resource, head toward closest not blocked by obstacle or opponent
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    if resources:
        best = None; bestd = 10**9
        for r in resources:
            rx, ry = r
            if (rx, ry) in obstacles:
                continue
            d = dist((sx, sy), (rx, ry))
            if d < bestd or (d == bestd and (rx, ry) < best if best else False):
                bestd = d; best = (rx, ry)
        if best is not None:
            rx, ry = best
            dx = 1 if rx > sx else -1 if rx < sx else 0
            dy = 1 if ry > sy else -1 if ry < sy else 0
            nx, ny = sx + dx, sy + dy
            if (nx, ny) == (ox, oy):
                dx, dy = 0, 0
            if inside(sx+dx, sy+dy) and (sx+dx, sy+dy) not in obstacles:
                return [dx, dy]
            return [0, 0]
    # Otherwise, move toward opponent or resources with simple rules
    # Prefer staying if blocked
    moves = [(dx, dy) for dx in (-1,0,1) for dy in (-1,0,1)]
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): continue
        if (nx, ny) in obstacles: continue
        score = 0
        # Encourage moving toward opponent
        if abs(nx - ox) + abs(ny - oy) < abs(sx - ox) + abs(sy - oy):
            score += 2
        # Avoid stepping into opponent square
        if (nx, ny) == (ox, oy):
            score -= 100
        if score > best_score:
            best_score = score; best_move = (dx, dy)
    # If all blocked, stay
    return [best_move[0], best_move[1]]