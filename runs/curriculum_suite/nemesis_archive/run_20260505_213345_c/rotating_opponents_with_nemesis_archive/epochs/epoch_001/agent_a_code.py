def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def dist2(a, b):
        dx = a[0]-b[0]
        dy = a[1]-b[1]
        return dx*dx + dy*dy

    # If on a resource, bias to stay (collecting is assumed by engine on landing)
    if (sx, sy) in set(tuple(p) for p in resources):
        return [0, 0]

    if not resources:
        # No resources: move away from opponent towards center-ish
        cx, cy = (w-1)/2.0, (h-1)/2.0
        best = (10**18, -10**18)
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = clamp(sx+dx, 0, w-1), clamp(sy+dy, 0, h-1)
            if (nx, ny) in obstacles:
                continue
            dcen = (nx-cx)*(nx-cx) + (ny-cy)*(ny-cy)
            dopp = dist2((nx, ny), (ox, oy))
            cand = (dcen, dopp)
            if cand < best:
                best = cand
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    res_set = set(tuple(p) for p in resources)

    best_key = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = clamp(sx+dx, 0, w-1), clamp(sy+dy, 0, h-1)
        if (nx, ny) in obstacles:
            continue
        # Distance to nearest resource
        dres = 10**18
        for rx, ry in res_set:
            dd = (nx-rx)*(nx-rx) + (ny-ry)*(ny-ry)
            if dd < dres:
                dres = dd
        # Distance to opponent (prefer being farther)
        dopp = dist2((nx, ny), (ox, oy))
        # Small bias to move if dres ties, prefer lexicographically smallest move among equal keys
        key = (dres, -dopp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]