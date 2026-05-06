def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Move away from opponent slightly to reduce contesting collisions
        dx = 0 if ox == sx else (1 if ox < sx else -1)
        dy = 0 if oy == sy else (1 if oy < sy else -1)
        return [-dx, -dy]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose resource that we can "claim" while also denying the opponent.
        local_best = -10**18
        for rx, ry in resources:
            my_d = abs(nx - rx) + abs(ny - ry)
            op_d = abs(ox - rx) + abs(oy - ry)
            # Reward being closer than opponent, but also keep making progress.
            # Small tie-breaker prefers moves that reduce distance to opponent slightly
            # when we are already winning the race to a resource.
            win_term = (op_d - my_d)
            progress_term = -my_d
            deny_term = 2 * win_term
            micro = -0.05 * (abs(nx - ox) + abs(ny - oy))
            val = deny_term + progress_term + micro
            if val > local_best:
                local_best = val

        # Prefer moves that avoid stepping into dead-end proximity to obstacles: penalize if surrounded.
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in obstacles:
                    adj_pen += 1
        local_best -= 0.03 * adj_pen

        if best_score is None or local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)
        elif local_best == best_score:
            # Deterministic tie-break: prefer staying still, then smaller dx, then smaller dy.
            if best_move != (0, 0) and (dx, dy) == (0, 0):
                best_move = (dx, dy)
            elif (dx, dy) != (0, 0) and best_move != (0, 0):
                if abs(dx) < abs(best_move[0]) or (abs(dx) == abs(best_move[0]) and abs(dy) < abs(best_move[1])):
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]