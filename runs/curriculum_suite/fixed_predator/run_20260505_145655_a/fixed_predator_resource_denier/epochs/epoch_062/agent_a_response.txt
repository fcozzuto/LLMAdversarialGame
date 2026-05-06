def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        deny = (od - sd) * 10 - sd
        center_bias = -(((rx - cx0) ** 2 + (ry - cy0) ** 2) * 1e-3)
        t = (deny + center_bias, -od, -sd, rx, ry)
        if best is None or t > best:
            best = t
    tx, ty = best[3], best[4]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    curr_sd = man(sx, sy, tx, ty)
    curr_od = man(ox, oy, tx, ty)
    best_m = None
    for dx, dy, nx, ny in moves:
        nd = man(nx, ny, tx, ty)
        # Primary: reduce our distance to the denied target; secondary: avoid drifting away.
        # Small tertiary: prefer staying closer to center to reduce corner traps.
        center_pen = ((nx - cx0) ** 2 + (ny - cy0) ** 2) * 1e-4
        # Also add slight preference for moves that put us in a better "net-deny" position vs opponent.
        net = (curr_od - nd) * 0.15
        mscore = (-nd * 2.0) + (-(nd - curr_sd) * 1.2) + net - center_pen
        cand = (mscore, -nd, dx == 0 and dy == 0, dx, dy)
        if best_m is None or cand > best_m:
            best_m = cand
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]