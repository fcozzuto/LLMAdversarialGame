def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx0 = (w - 1) * 0.5
    cy0 = (h - 1) * 0.5

    if not resources:
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            cb = -(nx - cx0) * (nx - cx0) - (ny - cy0) * (ny - cy0)
            k = (-cb, man(nx, ny, ox, oy), dx, dy)
            if k < best:
                best = k
        return [best[2], best[3]] if best else [0, 0]

    best_k = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_center = (nx - cx0) * (nx - cx0) + (ny - cy0) * (ny - cy0)

        # Interception/dynamic denial: maximize how much we outpace opponent for high-value resources,
        # and if we can't, minimize how close we allow them to get to any resource.
        gains = []
        min_opp = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Prefer resources where we can beat them now; otherwise punish states where opponent is very close.
            gains.append(opd - myd)
            if opd < min_opp:
                min_opp = opd

        gains.sort(reverse=True)
        top1 = gains[0] if gains else -10**6
        top2 = gains[1] if len(gains) > 1 else -10**6
        avg_top = (top1 + top2) * 0.5

        # If we are trailing everywhere, focus on blocking by pushing toward reducing opponent proximity.
        myd_to_opp = man(nx, ny, ox, oy)
        # Larger is better: outpace + deny closeness.
        score = (avg_top * 10.0) - (min_opp * 0.6) - (my_center * 0.01) - (myd_to_opp * 0.02)

        # Deterministic tie-break: prefer smaller manhattan to the best resource from this state.
        if gains:
            # approximate nearest-to-some-resource by min (man to all resources)
            my_min = min(man(nx, ny, rx, ry) for (rx, ry) in resources if (rx, ry) not in obstacles)
        else:
            my_min = 10**9

        k = (-score, my_min, dx, dy)
        if best_k is None or k < best_k:
            best_k = k
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]