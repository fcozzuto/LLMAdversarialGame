def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur = (sx, sy)
    opp = (ox, oy)

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_to_opp = md((nx, ny), opp)
            key = (d_to_opp, abs(ox - nx) + abs(oy - ny), dx == 0 and dy == 0, dx, dy)
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])] if best is not None else [0, 0]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        my_pos = (nx, ny)

        # Evaluate move by best "lead" over opponent among all resources.
        best_lead = None
        best_our = None
        for rx, ry in resources:
            rpos = (rx, ry)
            our_d = md(my_pos, rpos)
            opp_d = md(opp, rpos)
            lead = opp_d - our_d  # higher is better (we are closer)
            if best_lead is None or lead > best_lead or (lead == best_lead and our_d < best_our):
                best_lead = lead
                best_our = our_d

        # If no resource yields positive lead, still minimize our distance to the easiest one.
        # Tie-breakers: reduce distance to opponent slightly, prefer progress toward resource.
        d_opp_now = md(my_pos, opp)
        score = (-best_lead, best_our, d_opp_now, dx == 0 and dy == 0, abs(dx) + abs(dy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]