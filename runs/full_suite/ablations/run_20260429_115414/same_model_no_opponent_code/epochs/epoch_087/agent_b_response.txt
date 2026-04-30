def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        # Drift away from opponent deterministically
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = -cheb(nx, ny, ox, oy)
                cand = (score, dx, dy)
                if best is None or cand < best:
                    best = cand
        if best:
            return [best[1], best[2]]
        return [0, 0]

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        # If we can collect a resource immediately, strongly prefer it
        imm = -5 if (nx, ny) in res_set else 0

        best_adv = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = myd - 0.75 * opd  # lower is better: closer to target than opponent
            # Prefer targets not behind obstacles approximately by biasing if closer to direct line endpoints
            bias = 0
            if adv < (best_adv if best_adv is not None else 10**9):
                bias = 0
            cand_adv = adv + bias
            if best_adv is None or cand_adv < best_adv:
                best_adv = cand_adv

        # Additional tie-break: keep moving towards opponent when equal (blocks routes), else prefer improving own distance
        dist_to_opp = cheb(nx, ny, ox, oy)
        my_to_res = best_adv if best_adv is not None else 0
        score = my_to_res + imm - 0.05 * dist_to_opp
        cand = (score, dx, dy)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[1], best[2]]