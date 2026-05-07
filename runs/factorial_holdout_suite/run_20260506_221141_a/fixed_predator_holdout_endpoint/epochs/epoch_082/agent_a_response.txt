def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def cd(a, b, c, d):
        ax, ay = a - c, b - d
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    best_move = [0, 0]
    best_score = None

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate the best remaining target under this move: prefer getting there first,
        # then maximize lead over opponent, avoid very long trips.
        move_best = None
        for rx, ry in resources:
            sd = cd(nx, ny, rx, ry)
            od = cd(ox, oy, rx, ry)
            # Arrival advantage dominates; tie-break by smaller self distance, then deterministic ordering.
            val = (od - sd, -sd, -(rx + ry), -rx, -ry)
            if move_best is None or val > move_best:
                move_best = val

        # Small lookahead (1 more step) by biasing moves that keep decreasing our distance to chosen target.
        # Find the resource that maximizes our eval for this move and see next-step trend.
        chosen_dx = 0
        chosen_dy = 0
        if move_best is None:
            continue

        # To keep deterministic and compact, approximate trend using current move_best's implied sd via scanning again for same argmax.
        target = resources[0]
        target_best = None
        for rx, ry in resources:
            sd = cd(nx, ny, rx, ry)
            od = cd(ox, oy, rx, ry)
            val = (od - sd, -sd, -(rx + ry), -rx, -ry)
            if target_best is None or val > target_best:
                target_best = val
                target = (rx, ry)

        tx, ty = target
        d0 = cd(nx, ny, tx, ty)
        d1_best = None
        for ddx, ddy in moves:
            mx, my = nx + ddx, ny + ddy
            if 0 <= mx < w and 0 <= my < h and (mx, my) not in obstacles:
                dd = cd(mx, my, tx, ty)
                if d1_best is None or dd < d1_best:
                    d1_best = dd
        trend = (d1_best - d0) if d1_best is not None else 0  # more negative is better

        score = (move_best[0], move_best[1], -abs(trend), move_best[2], move_best[3], move_best[4])
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move