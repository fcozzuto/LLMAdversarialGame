def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    unclaimed = observation.get("unclaimed_cells") or []
    my_cells = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_cells = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    best_target = None
    if unclaimed:
        best_t = 10**9
        for x, y in unclaimed:
            x, y = int(x), int(y)
            if (x, y) in obstacles:
                continue
            t = (abs(x - cx) + abs(y - cy)) * 10
            t += abs(x - ox) + abs(y - oy)
            if t < best_t:
                best_t = t
                best_target = (x, y)

    if best_target is None:
        best_target = (int(round(cx)), int(round(cy)))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move, best_score = (0, 0), -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_target = abs(nx - best_target[0]) + abs(ny - best_target[1])

        if (nx, ny) in my_cells:
            cell_bonus = 0.0
        elif (nx, ny) in opp_cells:
            cell_bonus = 2.5  # likely flipping
        else:
            cell_bonus = 1.5  # unclaimed/neutral

        # prefer moving toward target; also slightly keep distance from opponent to avoid traps
        score = (-3.0 * d_target) + (-1.0 * d_center) + (0.15 * d_opp) + cell_bonus
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]