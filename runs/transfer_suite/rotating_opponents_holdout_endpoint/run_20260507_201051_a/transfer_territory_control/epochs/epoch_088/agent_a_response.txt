def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = {(int(x), int(y)) for x, y in self_t}
    opp_set = {(int(x), int(y)) for x, y in opp_t}
    unc_set = {(int(x), int(y)) for x, y in unclaimed}

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        for nx in (sx, sx + 1, sx - 1):
            for ny in (sy, sy + 1, sy - 1):
                if ok(nx, ny):
                    sx, sy = nx, ny
                    break
            else:
                continue
            break
        else:
            return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    center = (w - 1) / 2.0, (h - 1) / 2.0
    cx, cy = center

    # Precompute opponent territory centroid for mild directionality
    if opp_set:
        ax = sum(x for x, _ in opp_set) / len(opp_set)
        ay = sum(y for _, y in opp_set) / len(opp_set)
    else:
        ax, ay = ox, oy

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        dist_op = abs(nx - ox) + abs(ny - oy)
        dist_to_opp = abs(nx - ax) + abs(ny - ay)

        score = 0
        if (nx, ny) in opp_set:
            score += 2000  # immediate flip gain
        if (nx, ny) in unc_set:
            score += 50     # expansion
        if (nx, ny) in self_set:
            score -= 5      # avoid wasting moves

        # Favor approaching opponent territory area while not suicidally adjacent to opponent
        score += 30 * (-dist_to_opp)
        score += 5 * (dist_op)  # keep some spacing deterministically

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]