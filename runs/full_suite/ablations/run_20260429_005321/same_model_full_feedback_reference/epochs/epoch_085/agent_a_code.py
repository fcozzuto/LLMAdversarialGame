def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    if not resources:
        best = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                # keep away from opponent slightly and prefer center
                sc = (d2(nx, ny, ox, oy) - 0.1 * d2(nx, ny, w / 2, h / 2))
                if best == (0, 0) or sc > best[0]:
                    best = (sc, dx, dy)
        return [int(best[1]), int(best[2])]

    # Choose move that maximizes advantage to the best contestable resource.
    best_dx, best_dy = 0, 0
    best_score = -10**18
    center_x, center_y = (w - 1) / 2, (h - 1) / 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        my_best = 10**18
        my_prox = 10**18
        # Evaluate all resources deterministically; prefer those we can reach sooner than opponent.
        for rx, ry in resources:
            my = d2(nx, ny, rx, ry)
            opp = d2(ox, oy, rx, ry)
            adv = my - opp  # lower is better (we get there first)
            if adv < my_best:
                my_best = adv
                my_prox = my
            elif adv == my_best and my < my_prox:
                my_prox = my

        # Combine: strongest advantage first, then reduce our distance, then avoid opponent, then center.
        score = (-my_best) * 1000 - my_prox - 0.2 * d2(nx, ny, ox, oy) + 0.05 * d2(nx, ny, center_x, center_y) * (-1)
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]