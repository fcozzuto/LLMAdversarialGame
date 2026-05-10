def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick the resource that we are best positioned to beat (my distance vs opponent distance),
    # with deterministic tie-breaks.
    best_r = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # primary: we want to make (myd < opd) as strong as possible; i.e., minimize (myd - opd)
        # secondary: prefer smaller myd; tertiary: prefer smaller opd; final: lexicographic cell.
        key = (myd - opd, myd, opd, rx, ry)
        if best_r is None or key < best_r[0]:
            best_r = (key, (rx, ry))
    tx, ty = best_r[1]

    def valid_cell(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    # One-step lookahead: choose the move that most improves our ability to reach the chosen target
    # while also limiting opponent progress to that same target.
    best_mv = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid_cell(nx, ny):
            nx, ny = sx, sy  # engine behavior
        myd_n = man(nx, ny, tx, ty)
        opd_n = man(ox, oy, tx, ty)
        # If we can reduce our distance, prefer that; if opponent is already closer, try to close faster.
        # Tie-break with distance to the next-best resource overall to avoid getting stuck.
        # (deterministic and cheap)
        min_alt = 10**9
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            d = man(nx, ny, rx, ry)
            if d < min_alt:
                min_alt = d
        key = (myd_n - opd_n, myd_n, min_alt, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_mv = [dx, dy]

    return best_mv