def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Drift toward center while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Target resource that we can reach significantly earlier than opponent.
        best_r = None
        best_val = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                myd = 0
            # Encourage immediate advantage; slightly prefer closer-the-finish when ahead.
            lead = opd - myd
            reach_bias = -myd
            finish_bias = -cheb(ox, oy, rx, ry)
            val = (lead, reach_bias, finish_bias, -rx, -ry)
            if best_val is None or val > best_val:
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r

    # Greedily choose safe step maximizing advantage and minimizing distance to target.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Prefer moves that improve lead; if lead not improved, still reduce our distance.
        score = (opd2 - myd2, -myd2, -cheb(ox, oy, nx, ny), -abs(nx - tx) - abs(ny - ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all safe moves blocked (rare), try staying.
    return best_move