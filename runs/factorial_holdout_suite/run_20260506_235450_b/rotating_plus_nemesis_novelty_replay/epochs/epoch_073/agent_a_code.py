def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    res = []
    for r in resources:
        try:
            x, y = r
            if inb(x, y):
                res.append((x, y))
        except:
            pass
    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                sc = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
                if sc > best[0]:
                    best = (sc, dx, dy)
        return [best[1], best[2]]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (-10**18, 0, 0)
    for dx, dy, nx, ny in moves:
        if (nx, ny) in res:
            return [dx, dy]
        # choose target that maximizes our advantage (opp_d - self_d); if opponent unknown, just minimize self_d
        local_best = -10**18
        for rx, ry in res:
            self_d = abs(rx - nx) + abs(ry - ny)
            if opp_exists:
                opp_d = abs(rx - ox) + abs(ry - oy)
                adv = opp_d - self_d
                sc = adv * 1000 - self_d
            else:
                sc = -self_d
            if sc > local_best:
                local_best = sc
        if local_best > best[0]:
            best = (local_best, dx, dy)

    return [best[1], best[2]]