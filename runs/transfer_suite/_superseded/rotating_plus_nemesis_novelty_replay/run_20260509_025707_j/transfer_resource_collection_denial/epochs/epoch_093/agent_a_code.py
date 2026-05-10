def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cell_risk(x, y):
        # Penalty for being near obstacles (local dead-end avoidance)
        r = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    r += 2
        return r

    # If we're on a resource, stay unless it worsens capture advantage.
    cur_on = None
    for rx, ry in resources:
        if rx == sx and ry == sy:
            cur_on = (rx, ry)
            break
    if cur_on is not None:
        best = None
        best_adv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # Compute advantage for the best target under this move
            adv = -10**9
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                adv = max(adv, (od - sd, -sd))
            # Tie-break by lower risk
            key = (adv[0], adv[1], -cell_risk(nx, ny))
            if best is None or key > best:
                best = key
                best_move = [dx, dy]
        return best_move

    # Otherwise evaluate each candidate move by best achievable advantage across resources,
    # with strong preference for immediate collection (sd==0) and reduced obstacle risk.
    best_key = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        risk = cell_risk(nx, ny)
        # Find best advantage on this next cell
        best_adv = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # win-more measure: prefer becoming closer than opponent; immediate pickup dominates
            if sd == 0:
                adv = (10**6, 0, 0, man(nx, ny, rx, ry))
            else:
                adv = (od - sd, -sd, -(sd + man(nx, ny, rx, ry)), sd)
            if best_adv is None or adv > best_adv:
                best_adv = adv

        # Deterministic tie-break: prefer lower personal distance to the best resource
        key = (best_adv[0], best_adv[1], -risk, best_adv[3], (nx + ny))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move