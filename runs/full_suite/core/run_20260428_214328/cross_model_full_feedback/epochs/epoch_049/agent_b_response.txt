def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y):
                obst.add((x, y))

    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y) and (x, y) not in obst:
                res.append((x, y))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (0, 0)
    best_score = -10**18

    target = None
    if res:
        target = min(res, key=lambda p: dist((sx, sy), p))

    def near_to_opp(px, py):
        return dist((px, py), (ox, oy))

    # Score function: prefer moving towards nearest resource not blocked, then closer to opponent to pressure, then center bias
    def score_move(nx, ny):
        if not inside(nx, ny) or (nx, ny) in obst:
            return -10**6
        d_to_res = 0
        if target is not None:
            d_to_res = dist((nx, ny), target)
        opp_dist = dist((nx, ny), (ox, oy))
        # closer to resource is better (smaller d_to_res). If no resource, reduce to distance to opponent to pursue advantage.
        s = 0
        if res:
            s -= d_to_res * 4
        s -= opp_dist * 2
        # slight center pull
        cx, cy = w//2, h//2
        s -= dist((nx, ny), (cx, cy)) * 0.5
        return int(s)

    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        sc = score_move(nx, ny)
        if sc > best_score:
            best_score = sc
            best = (dx, dy)

    # Fallback: if blocked, stay
    dx, dy = best
    nx, ny = sx + dx, sy + dy
    if not inside(nx, ny) or (nx, ny) in obst:
        return [0, 0]
    return [dx, dy]