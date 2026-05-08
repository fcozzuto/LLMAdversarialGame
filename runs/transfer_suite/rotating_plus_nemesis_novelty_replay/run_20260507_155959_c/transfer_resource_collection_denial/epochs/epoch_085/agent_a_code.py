def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = None
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_key = (-10**9, -10**9, -10**9)
    # For each candidate move, evaluate the best resource we could aim for from next position.
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        my_best_adv = -10**9
        my_best_dist = 10**9
        my_best_opp = 10**9
        for rx, ry in resources:
            sd = md(nsx, nsy, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd  # higher means we are relatively closer
            if adv > my_best_adv or (adv == my_best_adv and (sd < my_best_dist or (sd == my_best_dist and od < my_best_opp))):
                my_best_adv, my_best_dist, my_best_opp = adv, sd, od
        # Tie-break: prioritize higher advantage, then smaller our distance, then smaller opponent distance
        key = (my_best_adv, -my_best_dist, -my_best_opp)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]