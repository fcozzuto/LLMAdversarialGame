def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if (d, dx, dy) < best:
                    best = (d, dx, dy)
        return [best[1], best[2]] if best[0] != 10**9 else [0, 0]

    res = [tuple(r) for r in resources]
    res_set = set(res)

    best_val = -10**30
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in res_set:
            val = 10**12
        else:
            # Choose the resource that favors us most after this move.
            # Larger is better: (opp_dist - our_dist), i.e., advantage in reaching first.
            best_adv = -10**30
            best_our = 10**9
            for rx, ry in res:
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                adv = opp_d - our_d
                if adv > best_adv or (adv == best_adv and our_d < best_our):
                    best_adv = adv
                    best_our = our_d
            # Encourage also getting closer when advantages tie.
            val = best_adv * 1000 - best_our

        # Deterministic tie-break: prefer smaller |dx|+|dy| then lexicographic.
        tie = (abs(dx) + abs(dy), dx, dy)
        cur = (val, -tie[0], -tie[1], -tie[2])
        best_cur = (best_val, - (abs(best_move[0]) + abs(best_move[1])), -best_move[0], -best_move[1])
        if cur > best_cur:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]