def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        for dx, dy in deltas:
            nx, ny = sx+dx, sy+dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def cheb(a, b, c, d):
        x = abs(a - c)
        y = abs(b - d)
        return x if x > y else y

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_target = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources closer to us than opponent; also value being closer overall.
        val = (ds - 0.9 * do, ds, do, rx, ry)
        if best_val is None or val < best_val:
            best_val = val
            best_target = (rx, ry)
    tx, ty = best_target

    # If opponent is extremely close to our best target, subtly bias against them by choosing
    # a nearby resource that is relatively better for us.
    if cheb(ox, oy, tx, ty) <= 1 and len(resources) > 1:
        alt = None
        alt_val = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = (ds - 1.2 * do, ds, abs(rx-tx)+abs(ry-ty), rx, ry)
            if alt_val is None or val < alt_val:
                alt_val = val
                alt = (rx, ry)
        if alt is not None:
            tx, ty = alt

    best_move = (0, 0)
    best_h = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist_to_target = cheb(nx, ny, tx, ty)
        dist_to_opp = cheb(nx, ny, ox, oy)
        # If adjacent to opponent, avoid giving them an easy capture route; otherwise chase target.
        opp_pen = 0
        if dist_to_opp == 0:
            opp_pen = 100
        elif dist_to_opp == 1:
            opp_pen = 12
        # Also prefer moves that reduce distance to target and slightly spread out from obstacles.
        hval = dist_to_target + 0.08 * dist_to_opp + opp_pen
        if best_h is None or hval < best_h:
            best_h = hval
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]