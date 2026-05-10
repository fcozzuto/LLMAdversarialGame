def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in (observation.get("resources") or [])]
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_val = -10**18
    for rx, ry in resources:
        md = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if (rx, ry) in obstacles:
            continue
        if md == 0:
            val = 10**7
        else:
            # Race: big reward if we arrive before opponent, penalty if not.
            advantage = od - md
            val = advantage * 200 - md
            # Prefer nearer resources overall.
            val += -0.5 * (md * md)
            # Slightly bias towards resources that are currently "farther" for opponent.
            val += 0.1 * (od * od)
            # If opponent can grab immediately, discourage this target.
            if od <= 1:
                val -= 10**4
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    cur_dist = man(sx, sy, tx, ty)

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        # Encourage decreasing distance; discourage moving onto squares that would
        # give opponent immediate access to that same target region.
        opp_d = man(ox, oy, tx, ty)
        score = (cur_dist - d) * 1000 - d
        if d == 0:
            score += 10**6
        # Mild obstacle/denial awareness: avoid stepping into dead-ends near obstacles
        # by checking how many neighboring obstacles we'd have.
        neigh_obs = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ex, ey = nx + adx, ny + ady
            if 0 <= ex < w and 0 <= ey < h and (ex, ey) in obstacles:
                neigh_obs += 1
        score -= neigh_obs * 3
        # Prefer staying if distance doesn't improve.
        if dx == 0 and dy == 0:
            score += 1
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]