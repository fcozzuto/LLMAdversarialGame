def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    best = (-(10**9), 10**9, 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        best_diff = -(10**9)
        best_res_dist = 10**9
        best_res = None

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            diff = opd - myd  # positive means we are closer
            if diff > best_diff or (diff == best_diff and myd < best_res_dist):
                best_diff = diff
                best_res_dist = myd
                best_res = (rx, ry)

        # Extra: avoid stepping into a cell where opponent would be closer than we are by too much.
        my_to_op = cheb(nx, ny, ox, oy)
        op_to_my = cheb(ox, oy, nx, ny)  # same under cheb, kept explicit for clarity
        threat = - (1 if my_to_op <= 1 else 0)

        # Tie-breaker: prefer moves that also reduce distance to opponent when we're winning on targeting.
        score = best_diff + threat
        score2 = best_res_dist
        if score > best[0] or (score == best[0] and (score2 < best[1] or (score2 == best[1] and (dx, dy) < (best[2], best[3])))):
            best = (score, score2, dx, dy)

    return [int(best[2]), int(best[3])]