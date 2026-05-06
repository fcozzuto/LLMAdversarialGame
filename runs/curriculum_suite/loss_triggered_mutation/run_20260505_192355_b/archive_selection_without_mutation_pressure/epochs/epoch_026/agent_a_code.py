def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy  # monotone with cheb; avoid sqrt

    best = None
    best_move = [0, 0]

    # Deterministic move ordering tie-break (already ordered moves); evaluate each candidate once.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Value is how much closer we are than opponent to a contested resource,
        # with a bias toward resources on the opponent's current "sweep" row.
        val = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Primary: maximize opponent - self (in squared metric), Secondary: prefer being closer to that resource.
            # Tertiary: prefer resources near opponent's row (sweep_rows counter).
            gain = opd - myd
            row_bias = abs(ry - oy)
            key = (gain, -myd, -row_bias)
            if val is None or key > val:
                val = key

        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return best_move