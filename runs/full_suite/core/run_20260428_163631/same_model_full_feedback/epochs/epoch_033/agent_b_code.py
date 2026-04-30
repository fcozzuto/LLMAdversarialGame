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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        # deterministic small bias toward center
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = (0, 0)
    best_val = None

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        # Evaluate by best resource advantage after this move
        worst_op_dist = 10**9
        best_adv = -10**9
        best_my_dist = 10**9

        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)

            # score favors being closer; slight preference for shorter absolute distance
            adv = (d_op - d_my) * 10 - d_my
            if adv > best_adv:
                best_adv = adv
            if d_my < best_my_dist:
                best_my_dist = d_my
            if d_op < worst_op_dist:
                worst_op_dist = d_op

        # discourage moves that allow opponent to be strictly closer everywhere
        val = best_adv + (best_my_dist == 0) * 50 + (-worst_op_dist) * 0.1

        if best_val is None or val > best_val:
            best_val = val
            best = (dxm, dym)
        elif val == best_val:
            # tie-break deterministic toward resources closer to us
            if cheb(sx + dxm, sy + dym, resources[0][0], resources[0][1]) < cheb(sx + best[0], sy + best[1], resources[0][0], resources[0][1]):
                best = (dxm, dym)

    return [int(best[0]), int(best[1])]