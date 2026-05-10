def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    if not resources:
        tx, ty = max(corners, key=lambda c: (man(ox, oy, c[0], c[1]) - man(sx, sy, c[0], c[1]), -c[0], -c[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res_set = set(tuple(p) for p in resources)

    best = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        got = 1 if (nx, ny) in res_set else 0
        # Choose the resource that would maximize our "arrival advantage" from (nx,ny).
        local_best_adv = -10**18
        local_best_dist = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds
            if adv > local_best_adv or (adv == local_best_adv and ds < local_best_dist):
                local_best_adv = adv
                local_best_dist = ds

        # Higher is better: winning head-start, then closer, then immediate pickup.
        score = got * 10**6 + local_best_adv * 1000 - local_best_dist
        if score > best or (score == best and [dx, dy] < best_move):
            best = score
            best_move = [dx, dy]

    return best_move