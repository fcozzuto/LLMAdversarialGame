def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    if not free(sx, sy):
        sx, sy = 0, 0
        if not free(sx, sy):
            return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # If no resources, drift toward opponent (to contest area).
    target_list = resources if resources else [(ox, oy)]

    # Select target where we are more advantaged vs opponent: (opponent_dist - my_dist), tie-breaker closer.
    best = None
    best_adv = -10**9
    best_myd = 10**9
    for rx, ry in target_list:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        if adv > best_adv or (adv == best_adv and myd < best_myd):
            best_adv = adv
            best_myd = myd
            best = (rx, ry)
    tx, ty = best

    # Local deterministic move choice among 9 deltas, avoiding obstacles.
    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # Primary: minimize distance to target; secondary: avoid moving away from target; also avoid giving opponent too much advantage.
            my_dist = cheb(nx, ny, tx, ty)
            opp_dist = cheb(ox, oy, tx, ty)
            my_adv = opp_dist - my_dist
            # Slightly discourage staying if movement can improve.
            stay_pen = 0 if (dx != 0 or dy != 0) else -0.1
            score = my_adv * 1000 - my_dist + stay_pen
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move