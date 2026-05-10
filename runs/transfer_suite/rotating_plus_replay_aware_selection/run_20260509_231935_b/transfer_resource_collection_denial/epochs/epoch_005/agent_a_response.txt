def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Prefer moves that let us secure the best remaining resource first, without stepping into obstacles.
    best = None
    best_val = -10**30

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # One-step lookahead: evaluate the best resource we could aim for from (nx, ny),
        # measured by distance advantage over opponent.
        cell_best = -10**30
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            if myd == 0:
                val = 10**9
            else:
                # Strongly prefer resources where we are closer; small penalty for taking longer.
                val = (opd - myd) * 100 - myd
            if val > cell_best:
                cell_best = val
        # Slight tie-break: prefer moves that also reduce our distance to the opponent.
        # (helps avoid being boxed when both chase same resource cluster)
        opp_prox = -md(nx, ny, ox, oy)
        val = cell_best + opp_prox
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best