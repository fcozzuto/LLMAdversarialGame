def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def line_block_penalty(x1, y1, x2, y2):
        # small deterministic penalty if moving into line-of-sight towards opponent across obstacles
        mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        p = 0
        for (oxb, oyb) in obstacles:
            if abs((oxb - mx)) + abs((oyb - my)) == 1:
                p += 1
        return p

    best_move = (0, 0)
    best_score = -10**18
    rlist = resources if resources else [(sx, sy)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        my_to_op = d2(nx, ny, ox, oy)
        # base: stay a bit away from opponent
        score = -2.2 * my_to_op - 0.15 * line_block_penalty(nx, ny, ox, oy)

        # choose best target advantage from this next position
        local_best = -10**18
        for (rx, ry) in rlist:
            if (rx, ry) == (sx, sy) and not resources:
                continue
            myd = d2(nx, ny, rx, ry)
            opd = d2(ox, oy, rx, ry)
            # advantage: prefer targets closer than opponent; also push toward picking resources
            # weights tuned to change strategy when behind (opd - myd negative)
            adv = (opd - myd)
            pick = -0.12 * myd
            steal_risk = 0.35 * (myd - opd)  # if I'm further than opponent, reduce
            # prefer nearer resources directly even when opponent is close
            val = 1.05 * adv + pick + steal_risk
            if val > local_best:
                local_best = val

        score += local_best

        # if opponent can immediately take a resource on next move, mitigate by moving closer to contested target
        if resources:
            contested = 0
            for (rx, ry) in resources:
                if d2(ox, oy, rx, ry) <= 2:
                    contested += 1
            if contested:
                score += 0.3 * (-contested) * d2(nx, ny, ox, oy) / 9.0

        # deterministic tie-break: lexicographic by move
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]