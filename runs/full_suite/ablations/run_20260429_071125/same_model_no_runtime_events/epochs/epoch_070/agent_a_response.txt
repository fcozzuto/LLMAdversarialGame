def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_obst(x, y):
        cnt = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if i == 0 and j == 0:
                    continue
                if (x + i, y + j) in obstacles:
                    cnt += 1
        return cnt

    # Choose best resource with a contest-aware heuristic
    best_r = None
    best_sc = None
    for rx, ry in resources:
        d_us = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Favor: close to us, far from opponent; slight preference to higher x/y for determinism
        sc = d_us - 0.85 * d_op + 0.001 * ((rx + ry) % 17)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_r = (rx, ry)
    tr, ty = best_r

    # Predict our best one-step move towards the target while reducing obstacle risk and avoiding tiles near opponent target.
    opponent_target = None
    opp_best = None
    for rx, ry in resources:
        d_op = cheb(ox, oy, rx, ry)
        if opp_best is None or d_op < opp_best:
            opp_best = d_op
            opponent_target = (rx, ry)
    orx, ory = opponent_target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_ms = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tr, ty)
        d_to_opp_t = cheb(nx, ny, orx, ory)
        # Lower is better; move towards our target, and slightly away from opponent's likely line
        ms = d_to_target + 0.25 * cheb(nx, ny, ox, oy) + 0.35 * adj_obst(nx, ny) - 0.06 * d_to_opp_t
        if best_ms is None or ms < best_ms:
            best_ms = ms
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]