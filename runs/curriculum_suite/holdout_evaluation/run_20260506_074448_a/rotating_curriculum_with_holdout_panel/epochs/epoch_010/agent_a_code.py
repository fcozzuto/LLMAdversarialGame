def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_targets = [(rx, ry) for (rx, ry) in resources if inb(rx, ry) and (rx, ry) not in obstacles]
    if not valid_targets:
        best = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            dctr = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
            key = (dctr, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        return best if best_key is not None else [0, 0]

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_best = None
        for tx, ty in valid_targets:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            lead = opd - myd  # positive means we are closer
            # Prefer winning proximity first; then closer; then farther from opponent for safety; then prefer fewer steps to some target
            # Also add small tie-break to reduce aimless wandering
            key_t = (lead, -myd, -cheb(nx, ny, ox, oy), -opd, -abs(nx - tx) - abs(ny - ty))
            if my_best is None or key_t > my_best[0]:
                my_best = (key_t, (tx, ty), myd, opd)
        if my_best is None:
            continue
        k = (-(my_best[0][0]), my_best[0][1], -my_best[0][2], my_best[0][3], dx, dy)  # convert to min-form
        if best_key is None or k < best_key:
            best_key = k
            best_move = [dx, dy]
    return best_move if best_key is not None else [0, 0]