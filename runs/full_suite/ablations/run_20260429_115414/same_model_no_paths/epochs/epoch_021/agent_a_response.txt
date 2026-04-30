def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If no resources, just head toward opponent diagonally/straight deterministically.
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Score by best contested resource: we want to arrive earlier than opponent.
        best_contest = -10**18
        best_our = 10**9
        for rx, ry in resources:
            our_t = md(nx, ny, rx, ry)
            opp_t = md(ox, oy, rx, ry)
            # Positive if we can beat opponent.
            contest = (opp_t - our_t) * 100 - our_t
            if contest > best_contest:
                best_contest = contest
            if our_t < best_our:
                best_our = our_t

        # Small penalty for increasing our distance to nearest resource and small incentive to reduce opponent distance.
        opp_dist = md(nx, ny, ox, oy)
        cur_opp_dist = md(sx, sy, ox, oy)
        opp_term = (cur_opp_dist - opp_dist) * 2

        score = best_contest + (-best_our) + opp_term

        # Deterministic tie-break: prefer (0,0), then smallest dx, then smallest dy.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            cand = (dx, dy)
            cur = best_move
            if cand == (0, 0) and cur != (0, 0):
                best_move = cand
            elif (cand != (0, 0)) and (cur != (0, 0)):
                if (cand[0], cand[1]) < (cur[0], cur[1]):
                    best_move = cand

    return [int(best_move[0]), int(best_move[1])]