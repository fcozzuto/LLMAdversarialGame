def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if resources:
        best_r = resources[0]
        best_adv = -10**9
        best_my = 10**9
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive = we are closer
            if adv > best_adv or (adv == best_adv and (myd < best_my or (myd == best_my and (rx, ry) < best_r))):
                best_adv, best_my, best_r = adv, myd, (rx, ry)
        tx, ty = best_r
        my_here = cheb(sx, sy, tx, ty)
        op_here = cheb(ox, oy, tx, ty)
        target_gain = my_here - op_here
    else:
        tx, ty = w // 2, h // 2
        target_gain = 0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # primary: minimize our distance and prefer resources where we keep an advantage
        score = (-myd) + 1.05 * (opd - myd)
        # secondary: reduce risk of being pinned by moving near opponent only if already winning
        if resources:
            dist_to_opp = cheb(nx, ny, ox, oy)
            score += (0.06 * dist_to_opp) if (opd - my_here) > 0 else (-0.02 * dist_to_opp)
        else:
            # if no resources, drift to center while keeping some distance from opponent
            score += (0.03 * (-cheb(nx, ny, w // 2, h // 2))) + (0.02 * cheb(nx, ny, ox, oy))

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]