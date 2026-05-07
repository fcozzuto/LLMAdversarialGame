def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    res = []
    for r in resources:
        try:
            x, y = r
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
        except:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def score_move(nx, ny):
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**18
        if not res:
            return 0
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in res:
            dm = abs(nx - rx) + abs(ny - ry)
            my_best = dm if dm < my_best else my_best
            if opp_exists:
                do = abs(ox - rx) + abs(oy - ry)
                opp_best = do if do < opp_best else opp_best

        # Prefer closer to resources, and strongly prefer resources where we're not behind.
        score = -my_best * 10
        if opp_exists:
            # For each resource, add advantage margin; take best.
            adv = -10**9
            for rx, ry in res:
                dm = abs(nx - rx) + abs(ny - ry)
                do = abs(ox - rx) + abs(oy - ry)
                # If we're closer (dm < do), advantage; otherwise discourage.
                m = (do - dm)
                if m > adv:
                    adv = m
            score += adv * 6
            # Mildly discourage moves that reduce opponent's best distance too much.
            opp_now = opp_best
            score -= (opp_now - opp_best) * 0  # keep deterministic/simple
        return score

    # Deterministic tie-break: smaller dx, then smaller dy by lexicographic on dirs order
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_move(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]