def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obst

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # If no resources, move to center to reduce pathing advantage loss.
    if not resources:
        cx, cy = w // 2, h // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            # deterministic tie-breaker: prefer smaller dx, then dy
            cand = (d, abs(dx) + abs(dy), dx, dy)
            if cand < best:
                best = cand
        return [best[2], best[3]]

    best = (-10**9, 10**9, 10**9, 0, 0)  # (adv, self_best_d, opp_best_d, dx, dy)
    # Choose move that maximizes win likelihood: advantage against opponent on best remaining resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        self_best_d = 10**9
        opp_best_d = 10**9
        adv_best = -10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > adv_best or (adv == adv_best and (sd < self_best_d or (sd == self_best_d and od < opp_best_d))):
                adv_best = adv
                self_best_d = sd
                opp_best_d = od
        cand = (adv_best, self_best_d, opp_best_d, dx, dy)
        if cand[0] > best[0] or (cand[0] == best[0] and cand[1] < best[1]) or (cand[0] == best[0] and cand[1] == best[1] and cand[2] < best[2]) or (cand[0] == best[0] and cand[1] == best[1] and cand[2] == best[2] and (cand[3], cand[4]) < (best[3], best[4])):
            best = cand

    return [best[3], best[4]]