def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (ox + sx) // 2, (oy + sy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, tx, ty)
            key = (d, man(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_move = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # choose move that gives maximal "advantage" over opponent for the best reachable resource
        best_resource_adv = None
        best_resource_dist = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # higher is better (we get closer than opponent)
            if best_resource_adv is None or adv > best_resource_adv or (adv == best_resource_adv and sd < best_resource_dist):
                best_resource_adv, best_resource_dist = adv, sd
        key = (-best_resource_adv, best_resource_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key, best_move = key, (dx, dy)

    return [best_move[0], best_move[1]]