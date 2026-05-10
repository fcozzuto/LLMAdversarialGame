def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obstacles_list)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Candidate move: avoid obstacles, then greedily maximize (we get there first)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target that beats opponent in deterministic way, with extra weight to contest their sweep row.
    best_t = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # Higher is better for us: we want do-ds positive and large.
        contest = 1.5 if ry == oy else 0.0
        # Also avoid "dead targets" that are behind obstacles by slight bias away from obstacle-adjacent tiles.
        adj_block = 0.0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (rx + ax, ry + ay) in obstacles:
                    adj_block = 0.6
        score = (do - ds) + contest - ds * 0.03 - adj_block
        # Deterministic tie-breaker
        key = (-score, ds + (0 if (rx, ry) == (sx, sy) else 0), rx, ry)
        if best_t is None or key < best_t[0]:
            best_t = (key, (rx, ry))

    tx, ty = best_t[1]

    # If opponent is closer to our best target, try to contest their row with another resource.
    ds0 = abs(tx - sx) + abs(ty - sy)
    do0 = abs(tx - ox) + abs(ty - oy)
    if do0 <= ds0:
        best2 = None
        for rx, ry in resources:
            if ry != oy:
                continue
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            contest = 2.0
            score = (do - ds) + contest - ds * 0.03
            key = (-score, ds, rx, ry)
            if best2 is None or key < best2[0]:
                best2 = (key, (rx, ry))
        if best2 is not None:
            tx, ty = best2[1]

    # Choose move that minimizes our distance to target, with slight priority to reduce opponent's options on their row.
    best_m = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = abs(tx - nx) + abs(ty - ny)

        # Opponent penalty: after this move, if we would step onto their sweep-contest row/col advantage.
        opp_term = 0.0
        if ny == oy:
            # Encourage reaching same row as their current y (contest), but only if we are not too far.
            opp_term = -0.25 * d_self

        # Small obstacle-aware bias: avoid moving next to obstacles.
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obstacles:
                    near_obs = 1
        near_term = 0.2 if near_obs else 0.0

        key = (d_self + near_term + (-opp_term), abs(tx - nx) + abs(ty - ny), rx if False else 0, nx, ny)
        if best_m is None or key < best_m[0]:
            best_m = (key, (dx, dy))

    if best_m is None:
        return [0, 0]
    return [int(best_m[1][0]), int(best_m[1][1])]