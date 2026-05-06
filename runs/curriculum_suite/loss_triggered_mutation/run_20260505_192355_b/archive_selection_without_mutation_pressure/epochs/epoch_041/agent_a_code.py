def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18
    best_tie = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        our_best = -10**18
        our_best_d = 10**9
        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            # Opponent archetype "sweep_rows": likely favors resources aligned with their row.
            row_adv = 3 if ry == oy else 0
            # Also mildly discourage giving them close access to near-row transitions.
            row_step = 1 if abs(ry - oy) == 1 else 0

            lead = (opp_d - our_d) - row_adv - row_step
            if lead > our_best or (lead == our_best and our_d < our_best_d):
                our_best = lead
                our_best_d = our_d

        # Prefer moves that keep us from wandering into clearly worse positions.
        cur_score = our_best
        if cur_score > best_score or (cur_score == best_score and our_best_d < best_tie):
            best_score = cur_score
            best_tie = our_best_d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]