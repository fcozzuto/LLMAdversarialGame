def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def nearest_score(px, py):
        if not res:
            return None, None, None
        best = None
        best_d = None
        for rx, ry in res:
            d = cheb(px, py, rx, ry)
            if best_d is None or d < best_d:
                best_d = d
                best = (rx, ry)
        return best, best_d, cheb(px, py, best[0], best[1]) if best is not None else None

    best_move = (0, 0)
    best_primary = None
    best_secondary = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if res:
            my_d_best = None
            opp_d_best = None
            best_adv = None
            # maximize "grabbing advantage": (opp distance - my distance) to best target
            for rx, ry in res:
                my_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                adv = opp_d - my_d
                if best_adv is None or adv > best_adv or (adv == best_adv and (my_d < my_d_best)):
                    best_adv = adv
                    my_d_best = my_d
                    opp_d_best = opp_d

            # secondary: prefer smaller my distance to the closest resource
            _, my_d_closest, _ = nearest_score(nx, ny)
            primary = best_adv
            secondary = my_d_closest
            # additional penalty if opponent is much closer to any resource than we are
            worst_gap = None
            for rx, ry in res:
                my_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                gap = my_d - opp_d  # negative => opponent closer
                if worst_gap is None or gap < worst_gap:
                    worst_gap = gap
            primary = primary + (0.01 * worst_gap)  # small deterministic bias
        else:
            # no resources: move to keep distance from opponent
            primary = cheb(nx, ny, ox, oy)
            secondary = abs(nx - ox) + abs(ny - oy)

        if best_primary is None or primary > best_primary or (primary == best_primary and (secondary < best_secondary)):
            best_primary = primary
            best_secondary = secondary
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]