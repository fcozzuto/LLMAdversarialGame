def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for t in observation.get("obstacles") or []:
        try:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose a target resource where we are relatively closer than opponent.
    # Score favors advantage, then shorter self distance.
    best_r = None
    best_r_score = None
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Strongly prefer resources we are closer to; also avoid tie traps.
            score = (do - ds) * 1000 - ds
            # If equal, slightly prefer ones that are far from opponent (harder to steal later).
            if do == ds:
                score -= (ds) * 2
            if best_r is None or score > best_r_score:
                best_r, best_r_score = (rx, ry), score

    # If no resources visible, drift toward opponent to reduce their options (defensive baseline).
    if not best_r:
        tx, ty = ox, oy
    else:
        tx, ty = best_r

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Immediate progress to target
        ns = cheb(nx, ny, tx, ty)
        cs = cheb(sx, sy, tx, ty)

        # Evaluate stealing risk: among remaining resources, how many are closer to opponent than us if we move here?
        steal_risk = 0
        if resources:
            for rx, ry in resources:
                if (rx, ry) == (tx, ty):
                    continue
                ds2 = cheb(nx, ny, rx, ry)
                do2 = cheb(ox, oy, rx, ry)
                if do2 < ds2:
                    steal_risk += 1

        # Value: minimize self distance, maximize progress, discourage moves that increase steal risk.
        # Also gently avoid moving away from target.
        val = -ns - (cs - ns) * 3 - steal_risk * 200

        # Tie-break: prefer staying or moving that reduces distance to opponent (prevents their runs)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move