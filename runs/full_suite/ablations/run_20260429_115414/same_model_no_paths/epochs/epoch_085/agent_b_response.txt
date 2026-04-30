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

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Choose a target resource that gives the best immediate advantage (we closer than opponent).
    opp_close = cheb(sx, sy, ox, oy) <= 2
    target = None
    target_adv = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = (opd - myd) - 0.1 * myd
        if adv > target_adv:
            target_adv = adv
            target = (rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        d_my_to_opp = cheb(nx, ny, ox, oy)
        if opp_close:
            # When opponent is near, prioritize spacing while not giving up too much progress.
            spacing_val = d_my_to_opp
        else:
            spacing_val = 0.5 * d_my_to_opp

        if resources and target is not None:
            rx, ry = target
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Encourage moving closer to the target and keeping/creating a lead.
            lead_val = (opd - myd) - 0.2 * myd
            # Light anti-trap: avoid stepping adjacent to obstacles if possible.
            adj_obs = 0
            for ex, ey in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ax, ay = nx + ex, ny + ey
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                    adj_obs += 1
            val = 5.0 * lead_val + 0.3 * spacing_val - 0.25 * adj_obs
        elif resources:
            # Fallback: minimize distance to nearest resource.
            myd_best = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < myd_best:
                    myd_best = d
            val = -1.5 * myd_best + 0.3 * spacing_val
        else:
            # No resources visible: drift away from opponent deterministically.
            val = 2.0 * spacing_val

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]