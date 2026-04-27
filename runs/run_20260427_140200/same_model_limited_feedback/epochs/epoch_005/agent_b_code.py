def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    # Pick a contested target: maximize opp_reach - self_reach (we want earlier access).
    best = None
    best_adv = None
    for rx, ry in resources:
        ds = cheb(rx, ry, sx, sy)
        do = cheb(rx, ry, ox, oy)
        adv = do - ds
        if best is None or adv > best_adv or (adv == best_adv and ds < best[0]):
            best = (ds, rx, ry)
            best_adv = adv
    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best[1], best[2]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Primary: get closer to target.
        d1 = cheb(nx, ny, tx, ty)
        # Secondary: avoid stepping into immediate opponent pressure.
        dist_opp = cheb(nx, ny, ox, oy)
        # Tertiary: prefer moves that increase advantage to the chosen target.
        ds_now = cheb(nx, ny, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        adv_now = do_now - ds_now
        score = (adv_now * 10) - d1 + (dist_opp == 1) * (-3) + (dist_opp >= 3) * 1
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]