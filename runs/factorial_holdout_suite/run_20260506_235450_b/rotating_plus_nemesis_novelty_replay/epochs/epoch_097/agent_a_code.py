def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    resources = observation.get("resources", []) or []
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    best_move = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # Evaluate this resulting position against all resources: prioritize being closer,
        # and when behind, prioritize denial (larger opp_d - my_d).
        best_cell_score = None
        best_cell_tie = None
        for tx, ty in resources:
            my_d = abs(tx - nx) + abs(ty - ny)
            if opp_exists:
                opp_d = abs(tx - ox) + abs(ty - oy)
                adv = opp_d - my_d
                # Advantage dominates; small tiebreak favors shorter my path to finish first.
                cell_score = (2 * adv) - (0.6 * my_d)
            else:
                cell_score = -my_d
            tie = (-(cell_score), my_d, tx, ty)
            if best_cell_score is None or tie < best_cell_tie:
                best_cell_score = cell_score
                best_cell_tie = tie

        # Also avoid getting stuck far from any resource: prefer smaller my_d for the chosen best cell.
        _, my_d_chosen, _, _ = best_cell_tie
        # Deterministic move preference order: lower my_d_chosen first, then dx, then dy.
        key = (my_d_chosen, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move