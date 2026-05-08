def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    resources = observation.get("resources") or []
    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                targets.append((x, y))
    if not targets:
        for p in unclaimed:
            if p is not None and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obs:
                    targets.append((x, y))

    def best_dist2(x, y, pts):
        d2 = None
        for a, b in pts:
            t = (a - x) * (a - x) + (b - y) * (b - y)
            if d2 is None or t < d2:
                d2 = t
        return d2 if d2 is not None else 0

    opp_d2 = (ox - sx) * (ox - sx) + (oy - sy) * (oy - sy)
    avoid = opp_d2 <= 9  # within 3 cells (approx)
    best_move = (0, 0)
    best_score = -10**18
    cur_t = best_dist2(sx, sy, targets)

    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d2 = best_dist2(nx, ny, targets) if targets else 0
        dist_improve = (cur_t - d2) if targets else 0

        nd2opp = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        opp_term = nd2opp - opp_d2

        score = 0
        score += 10 * dist_improve
        if avoid:
            score += 3 * opp_term  # move away if close
        else:
            score += -1 * opp_term  # slightly prefer moving toward if far

        score -= 0.1 * (dx * dx + dy * dy)  # prefer shorter moves deterministically
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]