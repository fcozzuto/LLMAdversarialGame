def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = moves

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    best_target = None
    best_adv = -10**9
    if resources:
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # higher means I'm closer than opponent
            if adv > best_adv or (adv == best_adv and (myd < cheb(sx, sy, *best_target) if best_target else True)):
                best_adv = adv
                best_target = (rx, ry)
    else:
        best_target = (ox, oy)  # fallback: keep space

    rx, ry = best_target
    best_move = (0, 0)
    best_score = -10**18

    my_opp_dist = cheb(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, rx, ry)
        # try to be hard to contest: also prefer moving away from opponent when not harming the goal too much
        nd = cheb(nx, ny, ox, oy)
        score = (-2.0 * myd) + (0.6 * nd) - (0.3 * obst_adj_pen(nx, ny))
        # strong preference to improve relative access when possible
        score += 0.8 * (cheb(sx, sy, rx, ry) - myd)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]