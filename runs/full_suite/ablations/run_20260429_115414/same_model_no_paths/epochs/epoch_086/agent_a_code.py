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
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_close = cheb(sx, sy, ox, oy) <= 2

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Prefer moves that secure/contest nearest resources relative to opponent.
        my_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            rel = opd - myd  # positive means we're closer now
            val = 5.0 * rel - 0.4 * myd + 0.15 * (rel > 0) - 0.02 * (rel < 0) * myd
            if myd == 0:
                val += 50.0  # immediate pickup
            my_best = val if val > my_best else my_best

        # If opponent is near, avoid giving them easy access: don't step adjacent to them
        # unless doing so also leads to an immediate pickup.
        adj = (max(abs(nx - ox), abs(ny - oy)) <= 1)
        if opp_close and adj and not any((nx == rx and ny == ry) for rx, ry in resources):
            my_best -= 12.0

        # Small bias toward reducing distance to opponent when we're already competitive (prevents being kited).
        rel_to_opp = cheb(nx, ny, ox, oy)
        my_best -= 0.05 * rel_to_opp if opp_close else 0.0

        if my_best > best_val:
            best_val = my_best
            best = (dx, dy)

    return [int(best[0]), int(best[1])]