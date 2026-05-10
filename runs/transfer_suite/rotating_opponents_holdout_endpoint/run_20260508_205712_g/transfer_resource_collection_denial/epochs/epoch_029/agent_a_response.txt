def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    res_set = set(tuple(p) for p in resources)

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_d = abs(nx - sx) + abs(ny - sy)
        myd = abs(nx - min(rx for rx, _ in resources)) + abs(ny - min(ry for _, ry in resources)) if resources else self_d
        # Compute best local target score by comparing to opponent for all resources (lightweight)
        my_best = 10**9
        op_best = 10**9
        gain = 0
        for rx, ry in resources:
            dme = abs(nx - rx) + abs(ny - ry)
            dob = abs(ox - rx) + abs(oy - ry)
            if dme < my_best:
                my_best = dme
            if dob < op_best:
                op_best = dob
            if (nx, ny) == (rx, ry):
                gain += 2000
        if not resources:
            op_dist = abs(ox - nx) + abs(oy - ny)
            my_dist = abs(sx - nx) + abs(sy - ny)
            score = (op_dist - my_dist) * 1000 - my_dist
        else:
            score = (op_best - my_best) * 1000 - my_best + gain
        # Prefer moving (reduce self_d) only as a small tiebreaker
        score -= self_d

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]