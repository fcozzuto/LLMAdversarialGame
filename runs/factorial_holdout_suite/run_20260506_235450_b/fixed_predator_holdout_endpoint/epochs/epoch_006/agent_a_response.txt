def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns = observation.get("turns_remaining", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            key = (-d, nx, ny)
            if key > best:
                best = key
                bx, by = dx, dy
        return [bx, by]

    # Strategy: deny by targeting resources where we can arrive earlier than opponent.
    # If no such resource exists, move toward the resource most likely to become stealable soon,
    # while slightly reducing distance to opponent (interception).
    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp_move = man(nx, ny, ox, oy)
        total = 0
        # Earlier arrival gets strong reward; later arrival gets penalty.
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # tighter advantage if close; encourage shortest steals
            if ds < do:
                # bonus rises as our lead increases and as distance decreases
                lead = do - ds
                total += 50 + 8 * lead - 2 * ds
            elif ds == do:
                total -= 15 + ds
            else:
                total -= 6 + 2 * (ds - do)
        # add small interception term: resource_denier archetype implies opponent contesting; reduce its access
        # (scaled down to avoid over-pursuing)
        intercept_weight = 1 if turns > 8 else 2
        total -= intercept_weight * (d_opp_move // 2)
        # deterministic tie-break: prefer larger total, then smaller distance to best resource in our favor
        if resources:
            nearest_win = 10**9
            for rx, ry in resources:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                if ds < do:
                    nearest_win = min(nearest_win, ds)
            total2 = total * 1000 - (nearest_win if nearest_win != 10**9 else 0)
        else:
            total2 = total * 1000
        key = (total2, -man(nx, ny, (w - 1) // 2, (h - 1) // 2), -dx, -dy, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move