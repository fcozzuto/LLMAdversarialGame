def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    best = (None, -10**18)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # For each move, pick best resource to target; score by guaranteed/contested reach.
        move_best = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # win first if we can arrive strictly earlier
            win = 1 if ds < do else 0
            # if equal arrival, still prefer closer for tie-break pressure
            margin = (do - ds)  # bigger is better
            # small preference for nearer absolute distance (finish quickly)
            val = (win, margin, -ds, -man(nx, ny, rx, ry))
            # lexicographic convert to scalar
            scalar = val[0] * 10**9 + val[1] * 10**6 + val[2] * 10**3 + val[3]
            if scalar > move_best:
                move_best = scalar

        # slight secondary: avoid wasting toward edge if tied
        if move_best > best[1]:
            best = ((dx, dy), move_best)

    if best[0] is None:
        return [0, 0]
    return [best[0][0], best[0][1]]