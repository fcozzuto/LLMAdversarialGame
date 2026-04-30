def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def safety(x, y):
        if (x, y) in occ:
            return -10**9
        pen = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            if (x+dx, y+dy) in occ:
                pen += 12
        for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            if (x+dx, y+dy) in occ:
                pen += 6
        return -pen

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    # Greedy "intercept" strategy: choose the next move that maximizes advantage on a contested resource,
    # while strongly discouraging positions adjacent to obstacles.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        s_base = safety(nx, ny)
        if s_base < -10**8:
            continue

        # If we are closer than opponent to some resource, prefer that resource; otherwise deny nearest.
        total = s_base
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)

            # Advantage component
            adv = (opd - myd)
            # Capture timing: small myd favored even if not strictly ahead
            timing = 14 - myd
            # Denial: if opponent is much closer, try to reduce their lead quickly
            denial = 0
            if opd <= myd:
                denial = - (myd - opd) * 18
            # Avoid resources extremely close to opponent to prevent immediate race loss
            opp_close = 1 if dist(ox, oy, rx, ry) <= 2 else 0
            penalty = opp_close * 40

            # Intercept bias: if after our move we head toward the midpoint between us and that resource,
            # we often create blocking pressure.
            mx = (rx + nx) // 2
            my = (ry + ny) // 2
            intercept = -dist(mx, my, ox, oy) * 0.5

            score = adv * 45 + timing * 6 + denial + intercept - penalty
            if score > local_best:
                local_best = score

        total += local_best
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]