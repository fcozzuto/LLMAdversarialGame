def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
        except:
            pass
    if not res:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    turn = int(observation.get("turn_index", 0) or 0)
    aggressive = (turn % 2 == 0)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_key = None
    tie_dirs = {(-1,-1):0,(0,-1):1,(1,-1):2,(-1,0):3,(0,0):4,(1,0):5,(-1,1):6,(0,1):7,(1,1):8}

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        my_pos = (nx, ny)
        opp_pos = (ox, oy)
        # Choose targets we'd likely reach first; if aggressive, bias more strongly to lead.
        best_t = None
        for rx, ry in res:
            t = (rx, ry)
            sd = cheb(my_pos, t)
            od = cheb(opp_pos, t)
            lead = od - sd  # positive means we are closer
            key = (lead, -sd, -od) if aggressive else (lead//2, -od, -sd)
            if best_t is None or key > best_t:
                best_t = key
        if best_t is None:
            continue
        # Prefer advancing (lower self distance) when tied.
        final_key = (best_t[0], best_t[1], best_t[2], -abs(nx-ox)-abs(ny-oy), -tie_dirs[(dx,dy)])
        if best_key is None or final_key > best_key:
            best_key = final_key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]