def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    sd0 = (sx, sy)
    od0 = (ox, oy)
    oppd = cheb(od0, sd0)

    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        s_time = cheb(sd0, (rx, ry))
        o_time = cheb(od0, (rx, ry))
        time_adv = o_time - s_time  # higher means we can arrive first (or later for opponent)
        # tie-break deterministically by resource position and closeness
        key = (time_adv, -s_time, -((rx * 29 + ry * 31) % 1000003))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        # out of bounds: score low; engine likely keeps in place, but be safe
        if not inb(nx, ny):
            mkey = (-10**9,)
        else:
            s_time = cheb((nx, ny), (tx, ty))
            o_time = cheb(od0, (tx, ty))
            time_adv = o_time - s_time

            # If we're not clearly winning the target, try to improve relative distance to opponent
            s_to_opp = cheb((nx, ny), od0)
            # Encourage approaching opponent when close, otherwise keep to resource race
            chase_bonus = 0
            if s_to_opp <= 2:
                chase_bonus = (oppd - s_to_opp)  # move that reduces gap gets higher

            # Prefer moves that reduce distance to target, slight bias by position
            dist_to_target = cheb((nx, ny), (tx, ty))
            bias = -((nx * 13 + ny * 17) % 997)

            mkey = (time_adv, -dist_to_target, chase_bonus, bias)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]