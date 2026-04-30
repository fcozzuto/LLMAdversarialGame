def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    def obstacle_pen(x, y):
        p = 0
        if (x, y) in occ: p += 10
        for dx, dy in adj8:
            if (x + dx, y + dy) in occ: p += 2
        return p

    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return -0.02 * (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5)

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            val = -man(nx, ny, ox, oy) + center_bias(nx, ny) - 3 * obstacle_pen(nx, ny)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    # Pick move that maximizes our post-move advantage over opponent for whichever resource we can contest best.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if resources:
            best_adv = None
            best_dist = None
            for rx, ry in resources:
                d_self = man(nx, ny, rx, ry)
                d_opp = man(ox, oy, rx, ry)
                adv = d_opp - d_self  # positive = opponent farther than us
                # Tie-break: prefer closer resource if advantage equal
                if best_adv is None or adv > best_adv or (adv == best_adv and d_self < best_dist):
                    best_adv, best_dist = adv, d_self
            val = best_adv + center_bias(nx, ny) - 0.06 * best_dist - 3.0 * obstacle_pen(nx, ny)
        else:
            val = center_bias(nx, ny) - 3.0 * obstacle_pen(nx, ny)
        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]] if best is not None else [0, 0]