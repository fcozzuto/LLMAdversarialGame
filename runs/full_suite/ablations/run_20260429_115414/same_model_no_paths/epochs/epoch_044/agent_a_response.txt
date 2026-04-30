def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_here = cheb(ox, oy, sx, sy)

    best_mv = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best = -10**18
        # Prefer actions that create a large distance advantage for us over opponent for some resource.
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # If opponent is already closer or equal, de-emphasize; else reward.
            adv = d_opp - d_my  # positive is good for us
            # Small tie-break: prefer shorter my distance once adv is similar.
            val = adv * 100 - d_my
            if val > my_best:
                my_best = val

        # If no resources, fall back to moving toward opponent (to block/contend area).
        if not resources:
            my_best = (cheb(nx, ny, ox, oy) < opp_here) * 10 - cheb(nx, ny, ox, oy)

        # Safety/obstacle-ish shaping: avoid moving to squares that are closer to opponent than we are.
        d_now_to_opp = cheb(sx, sy, ox, oy)
        d_new_to_opp = cheb(nx, ny, ox, oy)
        safety = (d_new_to_opp - d_now_to_opp)  # higher is safer
        val2 = my_best + safety

        if val2 > best_val:
            best_val = val2
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]