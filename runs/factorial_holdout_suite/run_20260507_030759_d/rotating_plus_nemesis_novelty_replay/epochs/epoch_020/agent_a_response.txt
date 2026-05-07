def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def score_cell(cx, cy):
        # higher is better
        my_d = abs(cx - sx) + abs(cy - sy)
        opp_d = abs(cx - ox) + abs(cy - oy)
        # prefer cells we can reach earlier; also prefer nearer overall when similarly contested
        return (opp_d - my_d) * 100 - my_d

    res_set = set(resources)
    # Precompute best target advantage from current position for stability
    best_now = None
    best_now_val = -10**18
    for rx, ry in resources:
        v = score_cell(rx, ry)
        if v > best_now_val:
            best_now_val = v
            best_now = (rx, ry)

    best_move = [0, 0]
    best_val = -10**18
    best_tie_d = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_val = -10**18
        # Immediate pickup bonus
        if (nx, ny) in res_set:
            move_val = 10**9

        # Evaluate next-position advantage across all resources
        for rx, ry in resources:
            my_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            v = (opp_d - my_d) * 100 - my_d
            # Encourage committing to the current best target unless a much better one appears
            if best_now is not None and (rx, ry) == best_now:
                v += 5
            if move_val < v:
                move_val = v

        # Deterministic tie-break: closer to best_now, then lower lex order by direction via dirs order
        tie_d = 10**9
        if best_now is not None:
            tie_d = abs(best_now[0] - nx) + abs(best_now[1] - ny)

        if move_val > best_val or (move_val == best_val and tie_d < best_tie_d):
            best_val = move_val
            best_tie_d = tie_d
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]