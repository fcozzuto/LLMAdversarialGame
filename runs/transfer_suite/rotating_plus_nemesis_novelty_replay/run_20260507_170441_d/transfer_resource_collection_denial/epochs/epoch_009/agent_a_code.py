def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {tuple(p) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # target: resource where we have the biggest distance advantage
    best_r = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        myd = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        adv = opd - myd
        if adv > best_adv or (adv == best_adv and (rx, ry) < tuple(best_r)):
            best_adv = adv
            best_r = [rx, ry]
    tx, ty = best_r

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # obstacle penalty radius
    def near_pen(x, y):
        if not obst:
            return 0
        p = 0
        for px, py in obst:
            if x == px and y == py:
                return -10**9
            dd = abs(x - px) + abs(y - py)
            if dd == 0:
                p += 10**8
            elif dd == 1:
                p += 6
            elif dd == 2:
                p += 2
        return -p

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        myd2 = d2(nx, ny, tx, ty)
        # also consider race on the best resource (not only target), cheap proxy:
        # compute our advantage on target after move vs opponent's current distance to that same target
        opd2 = d2(ox, oy, tx, ty)
        score = (opd2 - myd2)
        # encourage faster collection: reduce distance, and avoid stalling
        score += 0.1 * (d2(sx, sy, tx, ty) - myd2)
        # discourage moves that bring us closer to opponent when we can't win the target
        score -= 0.02 * d2(nx, ny, ox, oy)
        score += 0.5 * near_pen(nx, ny)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move