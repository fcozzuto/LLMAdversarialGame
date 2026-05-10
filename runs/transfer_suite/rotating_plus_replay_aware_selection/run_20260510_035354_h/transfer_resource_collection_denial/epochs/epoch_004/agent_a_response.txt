def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cell_value(rx, ry):
        if not inb(rx, ry) or (rx, ry) in obs:
            return 10**9
        myd = d(sx, sy, rx, ry)
        opd = d(ox, oy, rx, ry)
        # Prefer cells where we have a clear advantage; otherwise still move.
        race = myd - 1.7 * opd
        # If on opponent row/col, likely contested soon in denier mode.
        contest = (8 if ry == oy else 0) + (4 if rx == ox else 0)
        # Small center preference to keep options open.
        center = 0.01 * (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        return race + contest + center

    # Choose target resource deterministically by lexicographic key.
    best_rx, best_ry, best_key = resources[0][0], resources[0][1], None
    for rx, ry in resources:
        key = (cell_value(rx, ry), d(sx, sy, rx, ry), rx + ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    dx = 0 if best_rx == sx else (1 if best_rx > sx else -1)
    dy = 0 if best_ry == sy else (1 if best_ry > sy else -1)

    # Evaluate local move options; prefer diagonal if equally good.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m, best_score = (0, 0), None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Score by resulting distance-to-target and race at new position.
        myd = d(nx, ny, best_rx, best_ry)
        opd = d(ox, oy, best_rx, best_ry)
        sc = myd - 1.6 * opd + 0.001 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        key = (sc, abs(mx) + abs(my) == 0, -(mx == dx and my == dy), -abs(mx) - abs(my))
        if best_score is None or key < best_score:
            best_score = key
            best_m = (mx, my)

    return [int(best_m[0]), int(best_m[1])]