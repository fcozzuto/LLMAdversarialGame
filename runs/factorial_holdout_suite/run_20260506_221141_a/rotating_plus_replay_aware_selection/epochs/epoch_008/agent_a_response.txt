def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = None
        for dx, dy, nx, ny in valid:
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            tie = (abs(nx - ox) + abs(ny - oy))
            key = (-d, tie, nx, ny)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in valid:
        cell_best = None
        for rx, ry in resources:
            our = md(nx, ny, rx, ry)
            opp = md(ox, oy, rx, ry)
            adv = opp - our  # positive means we are closer
            # Prefer grabbing something closer (small our), and winning races (large adv).
            # Also slightly prefer resources that are closer to us if we can't win the race.
            immediate = 20 if our == 0 else (8 if our == 1 else 0)
            risk = 2 * (md(nx, ny, ox, oy))
            val = adv * 120 - our * 3 + immediate - risk * 0.1
            if cell_best is None or val > cell_best[0] or (val == cell_best[0] and (rx, ry) < cell_best[1]):
                cell_best = (val, (rx, ry))
        # Break ties by also keeping distance to opponent smaller (denial pressure), then lexicographic position
        _, (rx, ry) = cell_best
        opp_d = md(nx, ny, ox, oy)
        key = (cell_best[0], -opp_d, -md(nx, ny, gw - 1, gh - 1), -nx, -ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]