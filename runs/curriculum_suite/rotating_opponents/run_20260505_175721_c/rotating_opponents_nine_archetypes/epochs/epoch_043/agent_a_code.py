def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Score each move with a simple deterministic minimax-ish heuristic:
    # prioritize states where we are closer to key resources than the opponent,
    # while also slightly penalizing moves that give the opponent better access.
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        my_best = 10**9
        opp_best = 10**9
        my_adv_sum = 0
        opp_adv_sum = 0

        for (rx, ry) in resources:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            if d_me < my_best:
                my_best = d_me
            if d_op < opp_best:
                opp_best = d_op
            # Positive when we are closer than opponent on that resource.
            diff = d_op - d_me
            if diff >= 0:
                # Weight closer resources more; encourage denial.
                my_adv_sum += diff * 10 - d_me
            else:
                # Weight how badly we trail.
                opp_adv_sum += (-diff) * 6 + d_op

        # Additionally, prefer staying away from obstacles by rewarding higher local "free" mobility.
        free_nb = 0
        for tx, ty in cand:
            ax, ay = nx + tx, ny + ty
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                free_nb += 1

        val = (my_adv_sum - opp_adv_sum) + (my_best * -0.5) + (free_nb * 0.2) + (opp_best * -0.1)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]