def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def score_resource(r):
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        return od - sd

    # Pick best resource by advantage; ties by nearer to self then lexicographic.
    best = None
    best_key = None
    for r in resources:
        key = (score_resource(r), -dist((sx, sy), r), r[0], r[1])
        if best is None or key > best_key:
            best, best_key = r, key

    if best is None:
        tx, ty = (w//2, h//2)
    else:
        tx, ty = best

    # Candidate moves: avoid obstacles; prefer those that reduce distance to target.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), (tx, ty))
        # Secondary: also consider reducing opponent distance to their nearest resource (simple blocking).
        opp_best = None
        opp_bd = None
        for rr in resources:
            ad = dist((ox, oy), rr)
            if opp_best is None or ad < opp_bd:
                opp_best, opp_bd = rr, ad
        opp_target = opp_best if opp_best is not None else (w//2, h//2)
        opp_now = dist((ox, oy), opp_target)
        opp_after = dist((ox + (dx*0), oy + (dy*0)), opp_target)  # no change; keep deterministic
        mkey = (-d, opp_now - opp_after, dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]