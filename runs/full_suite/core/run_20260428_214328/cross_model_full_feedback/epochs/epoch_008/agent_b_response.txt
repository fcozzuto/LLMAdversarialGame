def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    # Gather valid moves
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
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

    # Prefer moving toward closest reachable resource not blocked
    best_r = None; best_d = 10**9
    for r in resources:
        try:
            rx, ry = r[0], r[1]
        except Exception:
            continue
        if not inside(rx, ry) or (rx, ry) in obstacles:
            continue
        # Manhattan distance
        d = abs(sx - rx) + abs(sy - ry)
        # If a candidate path can reach near resource, compute minimal steps to it
        if d < best_d:
            best_d = d; best_r = (rx, ry)
    if best_r is not None:
        rx, ry = best_r
        dx = 1 if rx > sx else -1 if rx < sx else 0
        dy = 1 if ry > sy else -1 if ry < sy else 0
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != (ox, oy):
            return [dx, dy]
        # blocked path to resource, fall back to safe move below

    # Otherwise, move to maximize distance from opponent while staying safe
    best = None; best_score = -10**9
    for dx, dy, nx, ny in candidates:
        # score: prefer closer to being far from opponent, and also approach closer to center to avoid traps
        odx = abs(nx - ox); ody = abs(ny - oy)
        dist_to_opp = odx + ody
        # secondary heuristic: prefer staying central
        center_dist = abs(nx - (w-1)/2) + abs(ny - (h-1)/2)
        score = dist_to_opp * 2 - center_dist
        if score > best_score or (score == best_score and (nx, ny) < (sx, sy)):
            best_score = score
            best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]

    return [0, 0]