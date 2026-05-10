def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = (-(10**9), 10**9, 10**9, 0, 0)  # (adv, myd, min_opd, rx, ry) for determinism

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        top_adv = -(10**9)
        top_myd = 10**9
        top_opd = 10**9
        top_rx = 0
        top_ry = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > top_adv or (adv == top_adv and (myd < top_myd or (myd == top_myd and (opd < top_opd or (opd == top_opd and (rx < top_rx or (rx == top_rx and ry < top_ry))))))):
                top_adv, top_myd, top_opd, top_rx, top_ry = adv, myd, opd, rx, ry

        cand = (top_adv, top_myd, top_opd, top_rx, top_ry)
        if cand > best:
            best = cand

    _, _, _, tx, ty = best
    # Step greedily toward the chosen best resource (still deterministic, obstacle-aware).
    tx = int(tx); ty = int(ty)
    best_step = [0, 0]
    best_dist = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_dist or (d == best_dist and (dx, dy) < (best_step[0], best_step[1])):
            best_dist = d
            best_step = [dx, dy]
    return [int(best_step[0]), int(best_step[1])]