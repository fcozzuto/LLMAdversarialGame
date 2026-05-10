def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    opp_pos = tuple(observation["opponent_position"])

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_counts(nx, ny):
        mya = 0
        oppa = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                t = (nx + dx, ny + dy)
                if t in self_t:
                    mya += 1
                elif t in opp_t:
                    oppa += 1
        return mya, oppa

    best_move = (0, 0)
    best_val = -10**18
    oppx, oppy = opp_pos

    # If unclaimed exists, bias toward near-center-of-unclaimed that is safer from opponent
    target_hint = None
    if unclaimed:
        def safe_key(c):
            cx, cy = c
            md = abs(cx - sx) + abs(cy - sy)
            # prefer cells near our territory and away from opponent
            my_adj = 0
            opp_adj = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    t = (cx + dx, cy + dy)
                    if t in self_t:
                        my_adj += 1
                    elif t in opp_t:
                        opp_adj += 1
            dist_opp = abs(cx - oppx) + abs(cy - oppy)
            return (-(my_adj), opp_adj, md, -dist_opp)
        target_hint = min(unclaimed, key=safe_key)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        mya, oppa = adj_counts(nx, ny)
        in_self = (nx, ny) in self_t
        in_opp = (nx, ny) in opp_t

        # Base reward: occupying/expanding
        if in_self:
            val = 2.0 + 0.7 * mya - 0.4 * oppa
        elif in_opp:
            # flipping opponent cell: value grows with our adjacency and when it reduces their frontier
            val = 10.0 + 1.8 * mya + 0.6 * (8 - oppa)
            # avoid suicidal flips next to many opponent cells unless we are well-connected
            val -= 0.8 * max(0, oppa - mya)
        else:
            # unclaimed: grow toward our territory, avoid being too exposed to opponent
            val = 4.0 + 1.2 * mya - 1.0 * oppa
            # slight bias toward the closest "good" unclaimed target hint
            if target_hint is not None:
                hx, hy = target_hint
                val += 0.05 * (abs(hx - oppx) + abs(hy - oppy)) - 0.03 * (abs(nx - hx) + abs(ny - hy))

        # Prefer moving generally away from being boxed in by opponent territory
        dist_from_opp = abs(nx - oppx) + abs(ny - oppy)
        val += 0.01 * dist_from_opp

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]