def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        margin = oppd - myd
        cent = -(abs(rx - cx) + abs(ry - cy))
        # Prefer resources where we are closer (margin >= 0), with biggest advantage.
        key = (0 if margin >= 0 else 1, -margin, myd, cent, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # If we are worse on all resources, lean into denial: target opponent's nearest resource.
    if best_key[0] == 1:
        opp_best = None
        opp_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            oppd = man(ox, oy, rx, ry)
            myd = man(sx, sy, rx, ry)
            key = (oppd, myd, rx, ry)
            if opp_key is None or key < opp_key:
                opp_key = key
                opp_best = (rx, ry)
        if opp_best is not None:
            tx, ty = opp_best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic: engine would also keep us
        nd = man(nx, ny, tx, ty)
        od = man(nx, ny, ox, oy)
        # Small tie-break towards center to avoid edge traps.
        cent = -(abs(nx - cx) + abs(ny - cy))
        val = (nd, -od, -cent, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]