def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best = (-10**18, -10**18, 10**18, 10**18)  # (adv, -self_dist, do, ds)
    best_move = [0, 0]
    res = [tuple(r) for r in resources]

    for dx0, dy0 in dirs:
        nx, ny = sx + dx0, sy + dy0
        if not valid(nx, ny):
            continue

        # pick the resource that gives us the strongest immediate race edge
        local_best = (-10**18, -10**18, 10**18, 10**18)
        for rx, ry in res:
            ds = max(abs(rx - nx), abs(ry - ny))
            do = max(abs(rx - ox), abs(ry - oy))
            adv = do - ds
            cand = (adv, -ds, do, ds)
            if cand > local_best:
                local_best = cand

        if local_best > best:
            best = local_best
            best_move = [dx0, dy0]

    return best_move