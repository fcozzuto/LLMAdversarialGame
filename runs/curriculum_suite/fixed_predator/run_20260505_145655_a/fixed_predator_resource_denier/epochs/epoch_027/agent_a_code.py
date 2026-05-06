def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_best = min(resources, key=lambda r: man((ox, oy), r))
    my_best = min(resources, key=lambda r: man((sx, sy), r))

    def deny_point():
        # Intercept near opponent's nearest resource (or stay put if already on it).
        rx, ry = opp_best
        dx = 0 if ox == rx else (1 if rx > ox else -1)
        dy = 0 if oy == ry else (1 if ry > oy else -1)
        return ox + dx, oy + dy

    intercept = deny_point()

    best_move = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        # Primary: win race to resources (advantage over opponent).
        for r in resources:
            sd = abs(nx - r[0]) + abs(ny - r[1])
            od = abs(ox - r[0]) + abs(oy - r[1])
            # Prefer states where we are closer and also closer in absolute terms.
            adv = od - sd
            sc += adv * 6 - sd * 0.8

        # Secondary: if opponent is likely to grab a resource first, move toward intercept.
        di = abs(nx - intercept[0]) + abs(ny - intercept[1])
        oi = abs(ox - intercept[0]) + abs(oy - intercept[1])
        sc += (oi - di) * 10 - di * 0.6

        # Tertiary: mild pull toward our nearest resource to avoid drifting.
        sc += (abs(ox - my_best[0]) + abs(oy - my_best[1]) - (abs(nx - my_best[0]) + abs(ny - my_best[1]))) * 2

        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]