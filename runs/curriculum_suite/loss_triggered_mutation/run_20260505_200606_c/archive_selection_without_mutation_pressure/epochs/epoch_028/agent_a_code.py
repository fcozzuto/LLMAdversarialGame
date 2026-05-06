def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    # Prefer going toward a resource where we can beat the opponent, with extra weight for matching the resource row.
    best_move = (0, 0)
    best_score = -10**18
    best_tiebreak = (10**9, 10**9, 10**9)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate this move against the most "dangerous" resource (one where opponent is closest).
        worst_case = 10**18
        best_local_adv = -10**18

        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            # If we are closer than opponent, that's good; otherwise it's bad.
            adv = (opp_d - our_d)

            # Row/col shaping: match resource row strongly, column weakly.
            row_gap = abs(ny - ry)
            col_gap = abs(nx - rx)
            shape = (8 if row_gap == 0 else 4 if row_gap == 1 else 1 if row_gap == 2 else 0)
            shape += (2 if col_gap == 0 else 1 if col_gap == 1 else 0)

            # Risk: how close opponent currently is compared to how close we are after this move.
            risk = (opp_d - our_d)

            # Combine:
            # - maximize advantage
            # - but penalize moves that let opponent be too dominant on some resource
            score_resource = adv * 10 + shape - (risk * 2)

            if score_resource < worst_case:
                worst_case = score_resource
            if score_resource > best_local_adv:
                best_local_adv = score_resource

        # Final score: balance average pressure (use worst_case) and best shot (best_local_adv).
        score = worst_case + (best_local_adv * 0.25)

        tiebreak = (abs(nx - ox) + abs(ny - oy), man(nx, ny, sx, sy), nx * 10 + ny)
        if score > best_score or (score == best_score and tiebreak < best_tiebreak):
            best_score = score
            best_move = (dx, dy)
            best_tiebreak = tiebreak

    return [int(best_move[0]), int(best_move[1])]