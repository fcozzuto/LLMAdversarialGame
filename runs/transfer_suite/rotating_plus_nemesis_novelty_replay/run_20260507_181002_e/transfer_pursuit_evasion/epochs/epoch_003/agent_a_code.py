def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def mobility(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if free(nx, ny):
                    c += 1
        return c

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Deterministic "escape corners" but with anti-zigzag: favor moves that both increase distance
    # and reduce the pursuer's immediate options (when we're evading) or reduce our distance
    # while increasing our mobility (when we're pursuing).
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: cheb((sx, sy), c) + 0.1 * cheb(c, (ox, oy)))

    best = None
    for dx, dy, nx, ny in moves:
        my_mob = mobility(nx, ny)
        opp_mob_here = mobility(ox, oy)  # stable; used only as tie-break signal

        d_cheb = cheb((nx, ny), (ox, oy))
        d_man = dist((nx, ny), (ox, oy))

        # Estimate pursuer ability next step: best distance pursuer could get if it moves greedily.
        if is_pursuer:
            # We're pursuer: choose state that minimizes distance to evader with obstacle-safe mobility.
            # Score: primary -cheb, secondary -man, tertiary +mobility, quaternary lexicographic.
            score = (-d_cheb, -d_man, my_mob, -abs(nx - target_corner[0]) - abs(ny - target_corner[1]), nx, ny)
        else:
            # We're evader: maximize distance; also prefer to move to "frontier" relative to corner
            # and avoid low-mobility dead-ends (zigzag opponents often capitalize on dead-ends).
            frontier = cheb((nx, ny), target_corner) - cheb((sx, sy), target_corner)
            # Score: primary +cheb, secondary +man, tertiary +mobility, quaternary +frontier.
            # Small penalty for moving into lower-mobility than opponent currently has.
            score = (d_cheb, d_man, my_mob - (opp_mob_here * 0.0), frontier, -nx, -ny)

        if best is None or score > best[0]:
            best = (score, [dx, dy])

    return best[1]