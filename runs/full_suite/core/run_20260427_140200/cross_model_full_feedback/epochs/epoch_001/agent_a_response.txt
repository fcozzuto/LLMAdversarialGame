def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    # Helpers
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for diagonal
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Select target resource
    my_best = None
    opp_best = None
    if resources:
        # Prefer resources I'm closer to than opponent; otherwise closest remaining.
        for r in resources:
            r = (r[0], r[1])
            dm = dist((sx, sy), r)
            do = dist((ox, oy), r)
            cand = (dm, do, r)
            if my_best is None or (do - dm, dm, do, r) < (my_best[0], my_best[1], my_best[2], my_best[3]):
                my_best = (do - dm, dm, do, r)
            if opp_best is None or (do, dm, r) < (opp_best[0], opp_best[1], opp_best[2]):
                opp_best = (do, dm, r)
        # If I can secure a resource (strictly closer), pick best such; else pick overall closest I can influence.
        my_strict = []
        for r in resources:
            r = (r[0], r[1])
            if dist((sx, sy), r) < dist((ox, oy), r):
                my_strict.append((dist((sx, sy), r), dist((ox, oy), r), r))
        if my_strict:
            my_strict.sort()
            target = my_strict[0][2]
        else:
            target = my_best[3]
    else:
        target = (w//2, h//2)
    # Evaluate candidate moves
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # Avoid giving opponent easy access by penalizing closeness after move
        d_to_target = dist((nx, ny), target)
        d_opp = dist((nx, ny), (ox, oy))
        # Progress: current distance minus new distance
        cur_d = dist((sx, sy), target)
        progress = cur_d - d_to_target
        # Resource capture bonus if landing on resource
        on_resource = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0
        # Encourage moving (slight) unless stuck
        move_cost = 0.02 if (dx == 0 and dy == 0) else 0.0
        score = (progress * 10) + (on_resource * 100) + (d_opp * 0.5) - (d_to_target * 0.2) - move_cost
        key = (score, -d_opp, -on_resource, -progress, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    if best is None:
        return [0, 0]
    return best[1]