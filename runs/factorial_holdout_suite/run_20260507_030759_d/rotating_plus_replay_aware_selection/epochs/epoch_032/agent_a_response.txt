def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Precompute closest resource distances from current positions
    self_d0 = []
    opp_d0 = []
    for (rx, ry) in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        self_d0.append(ds)
        opp_d0.append(do)

    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # For each resource compute advantage if we go to it next (one step already taken)
        # Score: maximize (opponent_dist - my_dist), prioritize capture now/soon, penalize giving opponent a faster capture.
        best_adv = -10**9
        best_cap = -10**9
        # threat: opponent can capture something significantly sooner than we can
        threat = 0
        # progress: how much we reduce our closest distance
        my_closest = 10**9

        for i, (rx, ry) in enumerate(resources):
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)

            if ds < my_closest:
                my_closest = ds

            adv = do - ds
            if adv > best_adv:
                best_adv = adv

            cap_bonus = 0
            if ds == 0:
                cap_bonus = 10000
            elif ds == 1:
                cap_bonus = 2000
            elif ds == 2:
                cap_bonus = 400
            if cap_bonus > best_cap:
                best_cap = cap_bonus

            # If opponent is much closer to a resource than we are, increase threat.
            # (Prefer moves that don't let opponent steal an otherwise close resource.)
            if do + 1 <= ds:
                # scale with how bad the mismatch is
                threat += (ds - do)

        # progress against our current closest distance
        my_closest0 = min(self_d0) if self_d0 else 10**9
        progress = my_closest0 - my_closest

        # Tie-breaks: capture first > higher advantage > more progress > lower threat > deterministic move order
        key = (best_cap, best_adv, progress, -threat, -abs(nx - sx) - abs(ny - sy))
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]