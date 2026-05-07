def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx >= dy else dy

    if not res:
        return [0, 0]

    # Pick a contested target: prefer resources we can reach no later than opponent.
    best = None
    best_key = None
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Primary: win margin (positive means we are earlier)
        # Secondary: smaller myd; Tertiary: farther from opponent (less likely to be immediately contested by pathing)
        key = (od - myd, -myd, cheb(ox, oy, sx, sy))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Choose move that reduces distance to target, while discouraging moving closer to opponent.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    best_move = None
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        myd_next = cheb(nx, ny, tx, ty)
        myd_now = cheb(sx, sy, tx, ty)
        # Encourage improvement first; if tied, maximize separation from opponent; then deterministic tie-break.
        sep_next = abs(nx - ox) + abs(ny - oy)
        improv = myd_now - myd_next  # positive if closer
        mkey = (improv, sep_next, -abs(dx), -abs(dy), dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]