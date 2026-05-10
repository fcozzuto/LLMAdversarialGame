def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    res = [tuple(r) for r in resources]
    res_set = set(res)

    # Contested resources: close to us OR close to opponent (near-term capture)
    near_opp = []
    for r in res:
        if man(ox, oy, r[0], r[1]) <= 2:
            near_opp.append(r)

    # Heuristic target: maximize opponent delay while we improve materially
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Row-sweep defense: if opponent is likely sweeping a row, prefer moving toward resources on that row
        row_pref = 0
        if ny == oy:
            row_pref = 2

        # If opponent is already very near some resource, avoid walking away from contesting that same area
        opp_catch_pen = 0
        for r in near_opp:
            if r in res_set:
                if man(ox, oy, r[0], r[1]) == 1 and man(nx, ny, r[0], r[1]) > 2:
                    opp_catch_pen = 6
                    break

        # Evaluate best immediate resource target from the candidate position
        best_target_val = None
        for r in res:
            if r in obs:
                continue
            sd = man(nx, ny, r[0], r[1])
            od = man(ox, oy, r[0], r[1])

            # Prefer resources on/near opponent row and those we can take soon
            row_bonus = 1 if r[1] == oy else 0
            soon_bonus = 3 if sd <= 1 else (1 if sd == 2 else 0)

            # Net score: we want (od - sd) large, plus being closer ourselves
            val = (od - sd) * 2 + row_bonus + soon_bonus - sd * 0.2
            if best_target_val is None or val > best_target_val:
                best_target_val = val

        total = best_target_val + row_pref - opp_catch_pen
        if best_val is None or total > best_val:
            best_val = total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]