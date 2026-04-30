def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obstacle_pen(x, y):
        pen = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) not in moves:
        moves.append((0, 0))

    def center_toward(x, y):
        cx, cy = (w - 1) // 2, (h - 1) // 2
        return man(x, y, cx, cy)

    if not resources:
        # Default: drift toward center while avoiding obstacles.
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (obstacle_pen(nx, ny), center_toward(nx, ny), abs(nx - ox) + abs(ny - oy))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) in resources:
            # Strongly prefer collecting if already on a resource.
            d_self = 0
        else:
            d_self = None

        # Evaluate by maximizing "positional advantage": how much closer we are than opponent to the best target.
        best_adv = -10**9
        best_target_dist = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_adv or (adv == best_adv and ds < best_target_dist):
                best_adv = adv
                best_target_dist = ds

        # Risk: moving too close to opponent is sometimes bad; small penalty for closeness.
        opp_close = man(nx, ny, ox, oy)
        # Also prefer reducing distance to our chosen target (implicitly best_adv tie-break).
        key = (
            -best_adv,                      # higher advantage first
            obstacle_pen(nx, ny),          # less obstacle proximity
            best_target_dist,              # closer to target
            opp_close,                     # not too close to opponent
            (nx + 31 * ny) % 7            # deterministic tie-break
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]