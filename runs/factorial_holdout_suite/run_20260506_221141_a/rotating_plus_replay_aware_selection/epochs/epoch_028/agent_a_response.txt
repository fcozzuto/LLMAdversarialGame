def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # If standing on a resource, or no resources exist, just hold or drift to center safely.
    if resources:
        best_score = -10**18
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue

            # Greedy one-step: evaluate resulting position vs closest contested resource.
            my_best = 10**9
            opp_best = 10**9
            my_t = None
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                if d_self < my_best:
                    my_best = d_self
                    my_t = (rx, ry)
                if d_opp < opp_best:
                    opp_best = d_opp

            if my_t is None:
                target_x, target_y = (gw - 1) // 2, (gh - 1) // 2
                d = cheb(nx, ny, target_x, target_y)
                score = -d
            else:
                target_x, target_y = my_t
                # Higher is better: prioritize resources we can reach first.
                d_self = cheb(nx, ny, target_x, target_y)
                d_opp = cheb(ox, oy, target_x, target_y)
                reach_adv = (d_opp - d_self)
                # Big bonus if we land on it.
                on_res = 1 if (nx, ny) == (target_x, target_y) else 0
                # Discourage stepping closer to opponent when contested (resource_denier).
                opp_dist = cheb(nx, ny, ox, oy)
                # Small mobility term to avoid traps.
                mob = 0
                for ddx, ddy in moves:
                    tx, ty = nx + ddx, ny + ddy
                    if legal(tx, ty):
                        mob += 1
                score = 1000000 * on_res + 50 * reach_adv + 1.5 * opp_dist + 0.2 * mob - 2.0 * d_self

            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # No resources: move toward center while maximizing safe mobility.
    cx, cy = (gw - 1) // 2, (gh - 1) // 2
    bestv = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, cx, cy)
        neigh = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if legal(tx, ty):
                neigh += 1
        v = -d + 0.4 * neigh + (0.01 if (dx, dy) != (0, 0) else 0.0)
        if v > bestv:
            bestv = v
            best_move = [dx, dy]
    return best_move