def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If there are resources, advance toward closest one while avoiding obstacles and keeping some distance from opponent.
    if resources:
        tx, ty = min(resources, key=lambda p: dist((p[0], p[1]), (mx, my)))
        best = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_bounds(nx, ny): 
                continue
            if (nx, ny) in obstacles:
                continue
            # Score: closer to target, further from opponent, and avoid landing on opponent
            d_t = dist((nx, ny), (tx, ty))
            d_o = dist((nx, ny), (ox, oy))
            if (nx, ny) == (ox, oy):
                # avoid opponent cell
                score = (10**6, -d_o)
            else:
                score = (d_t, -d_o)
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    # Fallback: stay or step away from opponent while staying within bounds and not on obstacle
    # Try small heuristic: move to a cell with maximal distance from opponent among valid moves
    best = (0, 0)
    best_dist = -1
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not in_bounds(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        d = dist((nx, ny), (ox, oy))
        if d > best_dist:
            best_dist = d
            best = (dx, dy)
    return [best[0], best[1]]