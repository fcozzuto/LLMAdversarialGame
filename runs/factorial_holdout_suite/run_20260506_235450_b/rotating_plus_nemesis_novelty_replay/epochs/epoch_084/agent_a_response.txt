def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass
    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**9, 0, 0)
        for dx, dy, nx, ny in moves:
            sc = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Rank resources: prefer those we can reach sooner and opponent can reach later.
    best_overall = (-10**18, 0, 0)
    for dx, dy, nx, ny in moves:
        best_r = (10**18, 10**18)
        for rx, ry in resources:
            ds = abs(rx - nx) + abs(ry - ny)
            if opp_exists:
                do = abs(rx - ox) + abs(ry - oy)
            else:
                do = ds + 1
            # Higher is better:
            # - prioritize ds
            # - discourage giving opponent a closer path
            # - small tie-break to move toward the nearest collectible overall
            sc = (do - ds) * 1000 - ds * 10 + (-(rx + ry) * 0 + 0)
            # Keep best resource score for this move
            if sc > best_r[0]:
                best_r = (sc, ds)
        sc_move = best_r[0]
        if sc_move > best_overall[0]:
            best_overall = (sc_move, dx, dy)
    return [best_overall[1], best_overall[2]]