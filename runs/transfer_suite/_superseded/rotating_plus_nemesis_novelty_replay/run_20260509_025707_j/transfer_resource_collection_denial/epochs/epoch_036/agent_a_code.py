def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list if p is not None and len(p) >= 2}

    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Evaluate this move by how much it improves our "win" over the nearest contestable resource.
        best_adv = -10**9
        best_my = 10**9
        best_rxry = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if not ok(rx, ry):
                continue
            my_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            adv = opp_d - my_d  # positive means we are closer than opponent
            # Prefer: larger advantage; then smaller my distance; then deterministic resource order
            if (adv > best_adv) or (adv == best_adv and (my_d < best_my or (my_d == best_my and (rx, ry) < (best_rxry if best_rxry is not None else (10**9, 10**9)) ))):
                best_adv = adv
                best_my = my_d
                best_rxry = (rx, ry)

        # If no resources, fall back to staying put.
        if best_rxry is None:
            val = (0, 0, 0)
        else:
            # Also slightly prefer moves that reduce our distance to the best resource we found.
            # Use tuple where larger is better for first component; encode into comparable form.
            val = (best_adv, -best_my, -(dx * 10 + dy))
        if best is None or val > best[0]:
            best = (val, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]