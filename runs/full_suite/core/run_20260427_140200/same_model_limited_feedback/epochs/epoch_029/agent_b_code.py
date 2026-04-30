def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [[-1,-1],[0,-1],[1,-1],[-1,0],[0,0],[1,0],[-1,1],[0,1],[1,1]]
    def cheb(a,b,c,d):
        dx = a-c if a>=c else c-a
        dy = b-d if b>=d else d-b
        return dx if dx>dy else dy
    # If no resources, drift toward center while avoiding obstacles if possible
    if not resources:
        tx, ty = w//2, h//2
        best = None
        for dx, dy in [(m[0],m[1]) for m in moves]:
            nx, ny = sx+dx, sy+dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles: 
                continue
            d = cheb(nx, ny, tx, ty)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        if best is None:
            return [0,0]
        return [best[1], best[2]]
    # Choose a resource that maximizes distance advantage
    opp_name = observation.get("opponent_name","opponent")
    best_r = None
    best_key = None
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        adv = d2 - d1
        key = (-adv, d1, (rx+ry) % 7)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    rx, ry = best_r
    # Step toward best resource, avoid obstacles; tie-break deterministically by move order
    best_move = None
    best_pair = None
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, rx, ry)
        # small preference for moves that also reduce opponent's distance to our target
        d_opp = cheb(ox, oy, rx, ry)
        pair = (d, -d_opp, i, dx, dy)
        if best_pair is None or pair < best_pair:
            best_pair = pair
            best_move = (dx, dy)
    if best_move is None:
        # All legal moves blocked by obstacles; stay
        return [0,0]
    return [int(best_move[0]), int(best_move[1])]