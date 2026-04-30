def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    if (sx, sy) in blocked:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def center_risk(x, y):
        # Small preference to stay away from corners late-game-ish via center distance
        return cheb(x, y, cx, cy)

    if not resources:
        # No visible resources: drift toward center, avoid obstacles.
        best = (10**9, 10**9, 10**9)
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                val = (center_risk(nx, ny), cheb(nx, ny, ox, oy), 0)
                if val < best:
                    best = val
                    best_move = [dx, dy]
        return best_move

    # Evaluate moves: prefer resources where we are not far behind opponent.
    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Choose best target for this move deterministically.
        best_res_val = 10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Main objective: get closer.
            val = myd * 100
            # If opponent is closer, discourage unless we're still very close.
            if opd < myd:
                val += (myd - opd) * 60 + 200
            # Tie-break: prefer resources where opponent is also far.
            val += (opd - myd if opd > myd else 0) * 5
            # Mild preference for picking up resources sooner in absolute terms.
            val += 0 if myd == 0 else myd
            if val < best_res_val or (val == best_res_val and (rx, ry) < best_res_xy):
                best_res_val = val
                best_res_xy = (rx, ry)

        # Also mildly avoid positions that let opponent approach us quickly.
        opp_approach = cheb(nx, ny, ox, oy)
        # Prefer not to be adjacent to opponent if equally good.
        move_val = (best_res_val, opp_approach, center_risk(nx, ny), dx, dy)
        if best is None or move_val < best:
            best = move_val
            best_move = [dx, dy]

    return best_move if best is not None else [0, 0]