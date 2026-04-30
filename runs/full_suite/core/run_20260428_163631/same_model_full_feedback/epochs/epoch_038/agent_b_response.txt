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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy, best_val = 0, 0, -10**18

    # If no resources visible, move to center to reduce distance churn.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > best_val:
                best_val, best_dx, best_dy = v, dx, dy
        return [best_dx, best_dy]

    # Deterministic tie-break: later resources in list slightly lower priority by adding a tiny index-based bias.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = 10**9
        opp_best = 10**9
        # Evaluate best net advantage from this next position
        for i, (rx, ry) in enumerate(resources):
            d_my = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer being closer than opponent; reward bigger lead; penalize letting opponent be closer.
            net = (d_opp - d_my)
            # Mild preference for immediate reach of a resource.
            net += 0.15 * (1 if d_my == 0 else (1.0 / (1 + d_my)))
            # Penalize wandering: smaller my distance to any resource.
            myd = d_my if d_my < myd else myd
            opp_best = d_opp if d_opp < opp_best else opp_best
            # Incorporate deterministic bias to break ties.
            net -= 0.0001 * i
            if net > opp_best:
                opp_best = net
        # Combine: best advantage plus slight pull toward nearest resource and away from opponent.
        nearest = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < nearest:
                nearest = d
        v = opp_best - 0.05 * nearest + 0.01 * cheb(nx, ny, ox, oy)
        if v > best_val:
            best_val, best_dx, best_dy = v, dx, dy

    return [int(best_dx), int(best_dy)]