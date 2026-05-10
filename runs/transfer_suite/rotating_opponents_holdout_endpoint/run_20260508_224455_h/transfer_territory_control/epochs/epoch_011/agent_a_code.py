def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", [])))
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    self_cnt = observation.get("self_territory_count", len(self_t))
    opp_cnt = observation.get("opponent_territory_count", len(opp_t))
    aggressive = 2.0 if opp_cnt < self_cnt + 1 else 1.2

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Precompute best unclaimed target (closest to us, then to center)
    best_unclaimed = None
    if unclaimed:
        best_unclaimed = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - cx) + abs(p[1] - cy)))

    best_move = [0, 0]
    best_v = -10**18

    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        pos = (nx, ny)

        v = 0.0

        # Core territory preferences
        if pos in opp_t:
            v += 1400.0 * aggressive
        elif pos in unclaimed:
            v += 260.0
        elif pos in self_t:
            v += 10.0
        else:
            v += 35.0

        # Expand toward closest unclaimed (front chasing)
        if best_unclaimed is not None:
            d_now = abs(sx - best_unclaimed[0]) + abs(sy - best_unclaimed[1])
            d_new = abs(nx - best_unclaimed[0]) + abs(ny - best_unclaimed[1])
            v += 6.0 * (d_now - d_new)

        # Avoid giving opponent immediate advantage: prefer moving away if it can't flip
        if pos not in opp_t:
            v += 0.8 * ((abs(sx - ox) + abs(sy - oy)) - (abs(nx - ox) + abs(ny - oy)))

        # Mild central control
        v += 1.2 * (((abs(sx - cx) + abs(sy - cy)) * -1.0) - ((abs(nx - cx) + abs(ny - cy)) * -1.0))

        if v > best_v:
            best_v = v
            best_move = [dx, dy]

    return best_move