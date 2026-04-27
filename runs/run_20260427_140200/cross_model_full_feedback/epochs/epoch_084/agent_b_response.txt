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

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = (0,0)
    best_score = -10**9

    # If there are resources, head toward nearest safe resource; else head toward center
    safe_positions = []
    for dx, dy in moves:
        nx, ny = mx+dx, my+dy
        if not in_bounds(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        safe_positions.append((dx, dy))

    if resources:
        nearest = min(resources, key=lambda r: dist((mx, my), r))
        for dx, dy in safe_positions:
            nx, ny = mx+dx, my+dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), nearest)
            # also punish getting too close to opponent
            od = dist((nx, ny), (ox, oy))
            score = -d*2 - (0 if od>1 else 100)
            if score > best_score:
                best_score = score
                best = (dx, dy)
        if best_score != -10**9:
            return [best[0], best[1]]
        # fallback to staying
        return [0,0]

    # no resources: move to minimize distance to center while avoiding obstacles and opponent
    center = (w//2, h//2)
    best = (0,0)
    best_score = -10**9
    for dx, dy in safe_positions:
        nx, ny = mx+dx, my+dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_center = dist((nx, ny), center)
        d_opp = dist((nx, ny), (ox, oy))
        score = -d_center*1.5 - d_opp
        if score > best_score:
            best_score = score
            best = (dx, dy)
    if best_score == -10**9:
        return [0,0]
    return [best[0], best[1]]