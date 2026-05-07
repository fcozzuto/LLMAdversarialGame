def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx; ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # Pick best resource by maximizing our advantage over opponent.
    def score_target(rx, ry, from_x, from_y):
        ds = cheb(from_x, from_y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we will arrive sooner; add tie-breaking.
        # Strongly discourage going where opponent is much closer.
        advantage = (do - ds)
        return advantage * 1000 + (4000 // (ds + 1)) - (rx + ry) * 3

    # If opponent is on a resource, we should avoid being denied next.
    opp_on_res = (ox, oy) in set(tuple(p) for p in resources)
    res_set = set(tuple(p) for p in resources)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = 0
        # Small preference to collect if we're stepping onto a resource.
        if (nx, ny) in res_set:
            v += 10**7
        # Evaluate after this move: target we should pursue.
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            local_best = max(local_best, score_target(rx, ry, nx, ny))
        v += local_best

        # If opponent is on a resource, reduce tendency to chase far resources;
        # instead prioritize nearest resource where we can be competitive.
        if opp_on_res:
            # Encourage shrinking our distance to the best competitive resource.
            min_ours = 10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                if do - ds >= 0:
                    if ds < min_ours:
                        min_ours = ds
            if min_ours < 10**9:
                v += (3000 // (min_ours + 1))

        # Tiny deterministic tie-break: prefer moves with smaller absolute deltas.
        v -= (abs(dx) + abs(dy)) * 0.001
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]