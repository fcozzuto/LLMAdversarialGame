def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((x, y) for x, y in observation.get("obstacles") or [])
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Evaluate best "capture target" with a deterministic tie-break.
        move_best = None
        for rx, ry in resources:
            d_s = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            # If we can reach at least as fast, strongly prefer.
            # Otherwise, prefer moves that reduce our disadvantage and increase opponent delay.
            if d_s <= d_o:
                val = (1000 - 10 * d_s) + (2 * d_o)  # capture/secure advantage
            else:
                val = (d_o - d_s) * 3 - d_s             # try to swing closer
            # Tie-break within resource by closeness to target first, then larger opponent distance.
            key = (val, -d_s, d_o)
            if move_best is None or key > move_best[0]:
                move_best = (key, rx, ry)

        # Secondary evaluation: how close we are to our selected target vs opponent's current.
        (key, rx, ry) = move_best
        d_s_now = cheb(nx, ny, rx, ry)
        d_o_now = cheb(ox, oy, rx, ry)

        # Global tie-break: prefer higher key, then lower our distance, then higher opponent distance, then lexicographic move.
        gkey = (key[0], -d_s_now, d_o_now, dx, dy)
        if best is None or gkey > best_key:
            best_key = gkey
            best = [dx, dy]

    return best