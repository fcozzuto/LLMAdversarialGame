def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Avoid stepping into immediate capture range of opponent
    safe_moves = []
    for dx, dy, nx, ny in legal:
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            continue
        safe_moves.append((dx, dy, nx, ny))
    if safe_moves:
        legal = safe_moves

    # If any resource exists, move toward closest resource while staying safe
    if resources:
        best = None
        best_score = None
        for dx, dy, nx, ny in legal:
            # distance to nearest resource
            dmin = min(dist((nx, ny), r) for r in resources)
            # prefer closer to resource and also keep distance from opponent
            o_dist = dist((nx, ny), (ox, oy))
            score = (dmin, o_dist)
            if best is None or score < best_score:
                best = (dx, dy, nx, ny)
                best_score = score
        if best:
            return [best[0], best[1]]

    # Fallback: move to reduce own distance to center while avoiding opponent
    center = (w//2, h//2)
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        d_to_center = dist((nx, ny), center)
        o_dist = dist((nx, ny), (ox, oy))
        score = (o_dist, d_to_center)
        if best is None or score < best_score:
            best = (dx, dy, nx, ny)
            best_score = score
    if best:
        return [best[0], best[1]]

    # Last resort
    return [0, 0]