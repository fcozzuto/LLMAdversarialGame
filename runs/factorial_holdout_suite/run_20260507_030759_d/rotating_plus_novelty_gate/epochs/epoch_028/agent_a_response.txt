def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(p[0], p[1]) for p in resources]
    if not res:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    res_set = set(res)
    best = None  # (score, dx, dy)
    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in res_set:
            return [dx, dy]

        best_for_move = None
        for rx, ry in sorted(res):
            our_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)

            # We want to arrive sooner; also deny by making opponent farther.
            # Slight preference for positions closer to some resource overall.
            immediate = 0
            if our_d == 0:
                immediate = 10**6
            val = (-our_d + (opp_d - our_d) * 0.7) + immediate

            # tie-break deterministically by target cell then by our_d
            tb = ( -val, rx, ry, our_d, opp_d)
            if best_for_move is None or tb < best_for_move[0]:
                best_for_move = (tb, val)

        # secondary tie-break: prefer smaller x then y of next position
        tb2 = (best_for_move[0][0], nx, ny, dx, dy)
        score = -tb2[0]
        cand = (score, dx, dy, tb2)
        if best is None or (cand[3] < best[3]):
            best = cand

    return [best[1], best[2]]