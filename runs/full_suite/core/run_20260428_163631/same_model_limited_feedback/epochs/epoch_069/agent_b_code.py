def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def best_resource():
        if not resources:
            return None
        best = None
        best_key = None
        for r in resources:
            rx, ry = r
            if (rx, ry) in obstacles:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Lower is better: prioritize closer and where opponent is relatively farther
            key = (ds - 0.85 * do, ds, (rx+ry))
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_resource()
    if target is None:
        return [0, 0]

    tx, ty = target
    cur = (sx, sy)
    best_dxdy = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        # discourage stepping into opponent proximity
        oppd = dist((nx, ny), (ox, oy))
        score = (nd, -oppd, (dx, dy))
        if best_score is None or score < best_score:
            best_score = score
            best_dxdy = (dx, dy)

    if best_dxdy is None:
        return [0, 0]
    return [int(best_dxdy[0]), int(best_dxdy[1])]