def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = [tuple(r) for r in observation.get("resources", []) if 0 <= r[0] < w and 0 <= r[1] < h and tuple(r) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    me = (sx, sy)
    opp = (ox, oy)
    trleft = int(observation.get("turns_remaining", 0))

    # If a resource is adjacent to opponent, prioritize denying by taking the closest such resource we can reach.
    threatened = [r for r in resources if man(r, opp) == 1]
    if threatened:
        best_tr = min(threatened, key=lambda r: (man(r, me), r[0], r[1]))
        best_move = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man((nx, ny), best_tr)
            if d < bestd or (d == bestd and (dx, dy) < best_move):
                bestd = d
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Otherwise, go for the resource we are most likely to secure first, based on turn horizon.
    # Evaluate each possible next move deterministically by a scoring heuristic.
    best_overall = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        next_pos = (nx, ny)
        d_opp_close = man(next_pos, opp)
        close_pen = 0
        if d_opp_close <= 1:
            close_pen -= 60 if d_opp_close == 1 else 120
        elif d_opp_close <= 2:
            close_pen -= 15

        # Find the best resource from this next position
        local_best = -10**18
        for r in resources:
            d_me = man(next_pos, r)
            d_op = man(opp, r)
            # Can we reasonably secure before/around opponent?
            # Tie-breakers by immediate advantage and closeness.
            secure = 1 if d_me <= d_op else 0
            horizon_bonus = 0
            if trleft > 0:
                # prefer resources that are reachable soonest within horizon
                if d_me <= trleft:
                    horizon_bonus = 10
                else:
                    horizon_bonus = -20
            # Resource value proxy: closeness, but strongly reward secure-when-closest
            val = (100 - d_me) + horizon_bonus + close_pen
            if secure:
                val += 80
                # mild push to not be behind if same distance
                if d_me == d_op:
                    val += 10
            else:
                # if opponent is strictly closer, prefer to be less behind
                val -= (d_me - d_op) * 8
            # add deterministic tie-break
            val += (-(r[0] * 2 + r[1]) * 0.0001)
            if val > local_best:
                local_best = val

        if local_best > best_score or (local_best == best_score and (dx, dy) < best_overall):
            best_score = local_best
            best_overall = (dx, dy)

    return [best_overall[0], best_overall[1]]