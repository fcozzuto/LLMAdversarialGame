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

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestk = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            k = (man(nx, ny, tx, ty), man(nx, ny, ox, oy))
            if bestk is None or k < bestk:
                bestk, best = k, (dx, dy)
        return [best[0], best[1]]

    # Interception: assume opponent targets the resource closest to it.
    targets = sorted(resources, key=lambda r: (man(r[0], r[1], ox, oy), man(r[0], r[1], sx, sy)))
    target = targets[0]
    tx, ty = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        self_d = man(nx, ny, tx, ty)
        opp_d = man(nx, ny, ox, oy)  # proxy for getting "in the way" near opponent
        # Advantage favors making it harder for opponent to reach this target.
        adv = (man(tx, ty, ox, oy) - self_d)
        k = (-adv, self_d, opp_d)
        if best_score is None or k < best_score:
            best_score, best_move = k, (dx, dy)

    return [best_move[0], best_move[1]]