def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # If no resources, head to center deterministically.
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    t = int(observation.get("turn_index", 0))
    best_score = None
    best_move = [0, 0]

    # Strategy change: score candidate next cells by "win probability proxy":
    # prefer cells where we beat opponent to some resource by a margin,
    # but also prefer approaching resources that the opponent can't reach first.
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue

        # tie-break stable: deterministic small hash on cell
        cell_tiebreak = (nx * 31 + ny * 17 + t) % 97

        best_for_this_cell = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs:
                continue
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)

            # prefer resources we can reach earlier; if not, prefer those where
            # opponent is close but still not decisively ahead.
            if my_d < op_d:
                win_flag = 0
                margin = op_d - my_d
            else:
                win_flag = 1
                margin = my_d - op_d  # smaller is better when not winning

            # also consider how close we are (and slightly penalize long walks)
            near = my_d
            # sweep-row nemesis proxy: resources on our current row/adjacent rows
            # get an extra push (opponent tends to sweep rows).
            row_bonus = 0
            if ry == sy or ry == sy + 1 or ry == sy - 1:
                row_bonus = -1

            key = (win_flag,
                   -margin,
                   near,
                   (rx * 7 + ry * 13) % 11,
                   row_bonus,
                   cell_tiebreak)
            if best_for_this_cell is None or key < best_for_this_cell:
                best_for_this_cell = key

        if best_for_this_cell is None:
            continue

        if best_score is None or best_for_this_cell < best_score:
            best_score = best_for_this_cell
            best_move = [mx, my]

    return best_move