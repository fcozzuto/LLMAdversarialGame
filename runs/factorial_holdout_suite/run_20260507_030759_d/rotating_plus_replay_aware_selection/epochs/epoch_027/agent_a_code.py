def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Score each move by best "secure" advantage over all resources, with tie-break by safety.
        # Aim: maximize (opp_dist - our_dist) heavily, but discourage moves that allow the opponent to arrive first/equal.
        move_best = (-10**18, 10**9, 10**9)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)

            adv = do - ds  # positive means we are closer
            # If opponent is at least as close, strongly penalize that resource as a target.
            contested_penalty = 0
            if do <= ds:
                contested_penalty = 2000 + (ds - do)

            # Also penalize overall slowness a bit to finish earlier and avoid giving time.
            finish_penalty = ds

            score = adv * 1000 - contested_penalty - finish_penalty

            # Tie-break: prefer more advantage, then smaller our distance to finish, then smaller opponent distance.
            key = (score, ds, do)
            if (key[0], -key[1], -key[2]) > (move_best[0], -move_best[1], -move_best[2]):
                move_best = (key[0], key[1], key[2])

        if (move_best[0], -move_best[1], -move_best[2]) > (best[0], -best[1], -best[2]):
            best = (move_best[0], move_best[1], move_best[2])
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]