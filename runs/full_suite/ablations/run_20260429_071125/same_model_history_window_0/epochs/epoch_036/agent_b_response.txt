def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    # If no resources, just move to reduce distance to opponent (deterministic)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        tx, ty = ox, oy
        best = None
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            d = dist((nx, ny), (tx, ty))
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]
    # Choose target resource where we are relatively closer than opponent
    best_t = None
    for r in resources:
        rd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        rel = rd - od
        # Prefer resources we can reach sooner; tie-break by absolute distance
        key = (rel, rd, r[0], r[1])
        if best_t is None or key < best_t[0]:
            best_t = (key, r)
    target = best_t[1]
    tx, ty = target
    best_move = None
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        # If we move onto/near target, also discourage moves that let opponent get closer to it
        # (single-step lookahead)
        opp_mvd = None
        for odx, ody in moves:
            anx, any = ox+odx, oy+ody
            if not inb(anx, any) or (anx, any) in obstacles:
                continue
            d2 = dist((anx, any), (tx, ty))
            if opp_mvd is None or d2 < opp_mvd:
                opp_mvd = d2
        if opp_mvd is None:
            opp_mvd = opd
        score = myd + 0.35 * max(0, opp_mvd - opd)  # lower is better
        # Small deterministic tie-break to avoid oscillation
        score_key = (score, abs(dx), abs(dy), nx, ny)
        if best_move is None or score_key < best_move[0]:
            best_move = (score_key, dx, dy)
    if best_move is None:
        return [0, 0]
    return [best_move[1], best_move[2]]