def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = w // 2, h // 2
        tx = cx if ox == cx else (0 if ox > cx else w - 1)
        ty = cy if oy == cy else (0 if oy > cy else h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    res = [(int(x), int(y)) for x, y in resources]

    # Current opponent closeness map
    opp_d = {r: man(ox, oy, r[0], r[1]) for r in res}

    best_move = [0, 0]
    best_score = -10**18
    any_lead = False

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Lead strategy: pick resource where we maximize (opp_dist - our_dist_after)
        lead = -10**18
        for r in res:
            od = opp_d[r]
            nd = man(nx, ny, r[0], r[1])
            s = (od - nd) * 10 - nd
            if s > lead:
                lead = s
        # lead is relative; determine if any move can secure positive lead against current opponent
        if lead > 0:
            any_lead = True
        # If cannot secure a lead, prioritize denying: go toward resource opponent is closest to
        if any_lead:
            score = lead
        else:
            # deny target: minimize our distance to the closest-to-opponent resource
            closest_to_opp = min(res, key=lambda r: (opp_d[r], r[0], r[1]))
            score = -man(nx, ny, closest_to_opp[0], closest_to_opp[1]) * 10 - closest_to_opp[0] * 0.001 - closest_to_opp[1] * 0.001
        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    if valid(sx + best_move[0], sy + best_move[1]):
        return best_move
    return [0, 0]