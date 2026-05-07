def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -(abs(nx - cx) + abs(ny - cy))
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Choose next cell that maximizes "win likelihood" over resources vs nearest-resource opponent
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell_score = -10**18
        for rx, ry in resources:
            myd = abs(rx - nx) + abs(ry - ny)
            if myd == 0:
                advantage = 10**9
            elif opp_exists:
                opd = abs(rx - ox) + abs(ry - oy)
                # Prefer resources where we're closer now (more advantage); tie-break by shorter myd
                advantage = (opd - myd) * 100 - myd
            else:
                advantage = -myd
            if advantage > cell_score:
                cell_score = advantage

        # Slight deterministic tie-break toward staying productive (reduce distance to best resource)
        # and avoid oscillations by favoring moves that reduce max(dx,dy) to 0 last.
        stab = - (abs(dx) + abs(dy) == 0) * 0  # keep deterministic without changing too much
        total = cell_score + stab
        if total > best[0]:
            best = (total, dx, dy)

    return [best[1], best[2]]