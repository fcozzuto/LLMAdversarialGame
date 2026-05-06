def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not res:
        best = min(candidates, key=lambda t: (man(t[2], t[3], ox, oy), t[0], t[1]))
        return [int(best[0]), int(best[1])]

    # Evaluate each move by its best resource target, prioritizing denial vs opponent.
    # score = (opp_closer?): maximize (opp_dist - my_dist), tie-break toward smaller my_dist.
    best = None
    for dx, dy, nx, ny in candidates:
        best_for_move = None
        for rx, ry in res:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # If we are closer, gain more; if opponent is closer, reduce their advantage.
            base = (opd - myd)
            # Small penalty for longer routes to avoid dithering.
            val = (base, -myd, rx, ry)
            if best_for_move is None or val > best_for_move:
                best_for_move = val
        # Tie-break deterministically by move deltas.
        key = (best_for_move, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]