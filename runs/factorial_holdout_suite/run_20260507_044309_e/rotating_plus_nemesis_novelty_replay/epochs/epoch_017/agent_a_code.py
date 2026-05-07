def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    w, h = observation["grid_width"], observation["grid_height"]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def dd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for diagonal movement

    # Pick a primary target where we can improve advantage (opponent distance minus our distance).
    primary = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dd(sx, sy, rx, ry)
        od = dd(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd)  # best advantage, then closest to secure
        if best_key is None or key > best_key:
            best_key = key
            primary = (rx, ry)

    if primary is None:
        return [0, 0]
    prx, pry = primary

    # Opponent closest resource (for mild denier).
    opp_best = None
    opp_sd_best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        od = dd(ox, oy, rx, ry)
        if opp_sd_best is None or od < opp_sd_best:
            opp_sd_best = od
            opp_best = (rx, ry)

    orx, ory = opp_best

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        our_d = dd(nx, ny, prx, pry)
        opp_d = dd(ox, oy, prx, pry)
        adv = opp_d - our_d

        # Deny: move closer to opponent's best target.
        deny_our = dd(nx, ny, orx, ory)
        deny_term = -deny_our

        # Small immediate incentive to step onto a resource.
        pickup = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0

        score = (adv * 1000) + (deny_term * 10) - our_d + pickup

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all candidate moves blocked, stay.
    return [best_move[0], best_move[1]]