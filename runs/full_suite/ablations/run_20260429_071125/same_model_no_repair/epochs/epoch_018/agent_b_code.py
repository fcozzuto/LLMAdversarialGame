def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def safe_pen(x, y):
        if (x, y) in occ:
            return 10**9
        pen = 0
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1)]:
            if (x+ax, y+ay) in occ:
                pen += 6
        for ax, ay in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            if (x+ax, y+ay) in occ:
                pen += 3
        return pen

    if not resources:
        return [0, 0]

    # Pick best target for which we have the biggest distance advantage, with safety bias.
    best_t = None
    best_sc = -10**18
    for rx, ry in resources:
        if (rx, ry) in occ:
            continue
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # Prefer resources where we can arrive sooner; also avoid resources very near opponent.
        opp_close = 1 if manh(rx, ry, ox, oy) <= 1 else 0
        sc = (opd - myd) * 40 - myd * 2 - opp_close * 35
        # Light bias toward closer-than-opponent with some obstacle avoidance near resource.
        if safe_pen(rx, ry) >= 10**8:
            sc -= 10**6
        sc -= safe_pen(rx, ry) * 2
        if sc > best_sc:
            best_sc = sc
            best_t = (rx, ry)

    tx, ty = best_t if best_t is not None else (sx, sy)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in occ:
            continue

        # Greedy approach: reduce my distance to target, keep/boost advantage over opponent.
        myd2 = manh(nx, ny, tx, ty)
        opd2 = manh(ox, oy, tx, ty)
        base = (opd2 - myd2) * 55 - myd2 * 1

        # Avoid stepping near opponent unless we have strong advantage.
        nd_opp = manh(nx, ny, ox, oy)
        opp_pen = 0
        if nd_opp <= 1:
            opp_pen = 70
        elif nd_opp == 2:
            opp_pen = 20

        # Safety + mild preference not to get stuck near obstacles.
        sp = safe_pen(nx, ny)
        if sp >= 10**8:
            continue

        # Slight smoothing: prefer moves that also reduce distance to any resource if target is bad.
        if best_sc < 0:
            anyd = min(manh(nx, ny, rx, ry) for rx, ry in resources if (rx, ry) not in occ)
            base -= anyd * 0.5

        val = base - opp_pen - sp * 1.2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]