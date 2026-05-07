def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d(a, b, c, d2):
        return max(abs(c - a), abs(d2 - b))

    tr = observation.get("turns_remaining", 0)
    best_move = [0, 0]
    best_val = -10**18

    # Deterministic tie-break: prefer moves with smaller (dx,dy) lexicographically if values equal.
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue

        # Score: maximize strongest resource we can secure before opponent;
        # if we can't secure any, minimize opponent's best lead over what they can secure.
        own_best = -10**18
        opp_best = 10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = d(nx, ny, rx, ry)
            ot = d(ox, oy, rx, ry)

            # Prefer resources sooner, strongly prefer resources we reach no later than opponent.
            if st <= ot:
                adv = ot - st
                # Encourage finishing before time runs out; de-emphasize far captures.
                time_term = (tr - st) if tr else 0
                val = 10**7 + adv * 10**5 + time_term * 10**3 - st * 30 - (rx + ry) * 0.01
                if val > own_best:
                    own_best = val
            else:
                lead = st - ot  # smaller is better (opponent earlier)
                val2 = lead * 10**5 + st * 40 + (rx + ry) * 0.01
                if val2 < opp_best:
                    opp_best = val2

        if own_best > -10**17:
            val = own_best
        else:
            # Can't beat opponent on any available resource now: push to reduce their lead.
            val = -opp_best

        if val > best_val or (val == best_val and (mdx, mdy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [mdx, mdy]

    return best_move