def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) not in obstacles:
            resources.append((rx, ry))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                nx, ny = sx, sy
            candidates.append((dx, dy, nx, ny))

    best_dxdy = (0, 0)
    best_val = None
    for dx, dy, nx, ny in candidates:
        my_best = -10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd
            center = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))  # closer to center => higher
            key = 5.0 * adv - 0.6 * myd + 0.08 * center
            if key > my_best:
                my_best = key
        # small tie-breaker: prefer moving toward center as center_rush opponent approaches
        tieb = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        val = my_best + 0.01 * tieb
        if best_val is None or val > best_val:
            best_val = val
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]