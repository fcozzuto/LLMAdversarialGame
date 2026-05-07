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

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # Central-ish drift while keeping distance to opponent
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = None
        for dx, dy, nx, ny in valid:
            key = ((nx - cx) ** 2 + (ny - cy) ** 2, man(ox, oy, nx, ny))
            # minimize distance to center, maximize distance from opponent
            score = (-key[1], -key[0])
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # One-step lookahead: for each move, evaluate strongest "win chance" resource.
    best = None
    for dx, dy, nx, ny in valid:
        best_adv = -10**9
        best_own = 10**9
        best_opp = 10**9
        for rx, ry in resources:
            our = man(nx, ny, rx, ry)
            opp = man(ox, oy, rx, ry)
            adv = opp - our  # positive -> we are closer
            if adv > best_adv or (adv == best_adv and our < best_own):
                best_adv = adv
                best_own = our
                best_opp = opp
        # Prefer moves that create advantage; if none, go toward nearest resource.
        score = (best_adv, -best_own, best_opp)
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]