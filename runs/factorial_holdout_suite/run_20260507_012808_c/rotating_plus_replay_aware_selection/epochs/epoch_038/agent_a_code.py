def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    if not resources:
        # drift to center-ish (deterministic)
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    opp = observation.get("opponent_position")
    ox, oy = opp[0], opp[1]

    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = 0
        if (nx, ny) in res_set:
            s += 10**6  # immediate pickup priority

        # Race advantage: maximize (opp_dist - my_dist) to the closest contested resource
        # with a small bias toward reducing my distance.
        max_adv = -10**9
        min_my_d = 10**9
        for rx, ry in resources:
            my_d = king_dist(nx, ny, rx, ry)
            opp_d = king_dist(ox, oy, rx, ry)
            adv = opp_d - my_d
            if adv > max_adv:
                max_adv = adv
            if my_d < min_my_d:
                min_my_d = my_d

        s += 2000 * max_adv
        s += -30 * min_my_d

        # Slightly prefer moving toward the board interior to avoid corner-trapping
        center_bias = -abs((nx - (w - 1) / 2)) - abs((ny - (h - 1) / 2))
        s += center_bias

        # Deterministic tie-break: prefer larger dx, then larger dy, then stay
        tie = (s, dx, dy) if best is not None else None
        if best is None or s > best_score or (s == best_score and (dx, dy) > (best[0], best[1])):
            best_score = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]