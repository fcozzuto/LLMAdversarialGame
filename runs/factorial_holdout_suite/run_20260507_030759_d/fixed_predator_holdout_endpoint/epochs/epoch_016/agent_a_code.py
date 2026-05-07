def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            d = max(abs(nx - tx), abs(ny - ty))
            cand = (d, abs(dx) + abs(dy))
            if best is None or cand < best:
                best = cand
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Resource-denial heuristic: pick the move that maximizes our advantage over the opponent
    # for the best (most favorable) resource after this step.
    best_overall = None
    best_move = (0, 0)

    for dx, dy, nx, ny in valid:
        my_best_adv = -10**9
        my_best_dist = 10**9
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            adv = od - sd  # positive means we are closer than opponent
            if adv > my_best_adv or (adv == my_best_adv and sd < my_best_dist):
                my_best_adv = adv
                my_best_dist = sd
        # Tie-break: prefer staying closer to resources (avoid moving away) deterministically.
        score = (my_best_adv, -my_best_dist, -(abs(nx - sx) + abs(ny - sy)), dx, dy)
        if best_overall is None or score > best_overall:
            best_overall = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]