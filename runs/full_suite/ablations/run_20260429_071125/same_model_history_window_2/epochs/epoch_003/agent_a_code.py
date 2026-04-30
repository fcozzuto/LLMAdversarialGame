def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            key = (-d, dx, dy)  # smaller is better for key; we want closer -> larger -d
            if best is None or key < best:
                best = key
        if best is None:
            return [0, 0]
        return [int(best[1]), int(best[2])]

    res = [(r[0], r[1]) for r in resources]
    cur_to_opp = man(sx, sy, ox, oy)

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        our_d_opp = man(nx, ny, ox, oy)
        opp_pressure = 0
        if our_d_opp <= cur_to_opp:
            opp_pressure = 1  # don't drift too far from blocking center

        best_resource = -10**18
        for rx, ry in res:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            gap = opp_d - our_d  # positive means we are closer than opponent at this move
            # Encourage being the next best collector and winning races; discourage giving opponent easy gaps
            val = gap * 30 - our_d * 2 + (10 if our_d == 0 else 0) - (10 if gap < 0 and opp_d == our_d else 0)
            # Prefer resources not behind the opponent relative to us
            val -= 3 * (1 if our_d > opp_d and opp_d <= our_d + 1 else 0)
            if val > best_resource:
                best_resource = val

        # Slightly prefer moves that reduce distance to the best resource (greedy tie-break)
        # Deterministic tie-break by lexicographic (dx,dy) after score.
        key = (-best_resource - opp_pressure, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]