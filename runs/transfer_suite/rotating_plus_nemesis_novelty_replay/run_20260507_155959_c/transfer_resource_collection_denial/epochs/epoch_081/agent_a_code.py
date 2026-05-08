def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (dx != 0 or dy != 0) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if (0, 0) not in obs:
        moves.append((0, 0))
    if not moves:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            # prefer center while keeping away from opponent a bit deterministically
            val = (abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy))
            if best is None or val < best[0]:
                best = (val, (dx, dy))
        return [best[1][0], best[1][1]]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # evaluate each move by whether we become relatively closer to the best contested resource
    best_move = (0, 0)
    best_score = None
    best_my = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        my_best_delta = -10**18
        my_best_dist = 10**18
        for r in resources:
            rx, ry = r[0], r[1]
            myd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            delta = oppd - myd  # higher means we are closer than opponent for that resource
            if delta > my_best_delta or (delta == my_best_delta and myd < my_best_dist):
                my_best_delta = delta
                my_best_dist = myd
        # choose move that maximizes relative advantage; tie-break: shorter my distance; then lexicographic
        cand = (my_best_delta, -my_best_dist, -dx, -dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = (dx, dy)
            best_my = my_best_dist

    return [best_move[0], best_move[1]]