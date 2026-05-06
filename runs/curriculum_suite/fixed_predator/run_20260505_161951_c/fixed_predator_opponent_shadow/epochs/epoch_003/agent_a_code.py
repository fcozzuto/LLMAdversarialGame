def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        best_d = -10**18
        best = (0, 0)
        for dx, dy, nx, ny in moves:
            d = abs(nx - ox) + abs(ny - oy)
            if d > best_d:
                best_d, best = d, (dx, dy)
        return [best[0], best[1]]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy, nx, ny in moves:
        self_pos = (nx, ny)
        cur_best = -10**18
        for rx, ry in resources:
            r = (rx, ry)
            ds = man(self_pos, r)
            do = man((ox, oy), r)
            # prefer resources where we are much closer than opponent
            # add small bias for being closer overall, and penalize being too far
            adv = (do - ds) * 100 - ds
            if adv > cur_best:
                cur_best = adv
        if cur_best > best_score:
            best_score, best_move = cur_best, (dx, dy)

    return [best_move[0], best_move[1]]