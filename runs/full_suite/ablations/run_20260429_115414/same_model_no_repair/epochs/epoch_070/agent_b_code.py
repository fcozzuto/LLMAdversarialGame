def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def passable(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def min_obst(x, y):
        if not obstacles:
            return 99
        best = 10**9
        for (px, py) in obstacles:
            d = cheb(x, y, px, py)
            if d < best: best = d
        return best

    # Choose a target resource: prefer one where we have relative advantage.
    if resources:
        best_res = None
        best_adv = -10**18
        best_dist = 10**18
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer
            if adv > best_adv or (adv == best_adv and myd < best_dist):
                best_adv = adv
                best_dist = myd
                best_res = (rx, ry)
        # If we have no advantage, still go to the closest resource deterministically.
        if best_adv <= 0:
            best_res = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
    else:
        best_res = (w // 2, h // 2)

    rx, ry = best_res
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if passable(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Score moves: get closer to target; increase opponent distance to same target;
    # keep away from obstacles; slight preference for staying closer to the current line toward target.
    best_move = (0, 0)
    best_val = -10**18
    cur_myd = cheb(sx, sy, rx, ry)
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        oppd_next = cheb(nx, ny, ox, oy)  # move that improves relative position against opponent
        obstacle_keep = min_obst(nx, ny)
        # Main: reduce distance to target and not allow opponent to be much closer (proxy).
        val = (cur_myd - myd) * 6 + (opd - myd) * 1.5 + obstacle_keep * 0.15 + oppd_next * 0.02
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]