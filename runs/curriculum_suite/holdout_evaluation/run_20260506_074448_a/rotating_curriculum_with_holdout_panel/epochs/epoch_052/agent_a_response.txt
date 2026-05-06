def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Determine opponent's best next resource (where they have the shortest distance).
    best_opp_res = None
    best_opp_d = 10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = man(ox, oy, rx, ry)
        if d < best_opp_d:
            best_opp_d = d
            best_opp_res = (rx, ry)

    # Determine "stealable/contested" resource: one where we can arrive no later than opponent after this move.
    contested = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        contested.append((rx, ry, myd - od))

    # Score each move as: maximize our ability to beat opponent at their nearest resource,
    # otherwise maximize reaching any resource before they do, with mild center bias.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Hard preference: if move lands on a resource.
        on_res = 0
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                on_res = 1
                break

        # Compete directly on opponent's nearest resource.
        if best_opp_res is not None:
            tx, ty = best_opp_res
            myd_to_opp = man(nx, ny, tx, ty)
            od_to_opp = best_opp_d
            race = od_to_opp - myd_to_opp  # positive means we are closer than they are currently
        else:
            race = 0

        # Also consider any resource where we can catch up soon.
        catch = -10**9
        for rx, ry, diff in contested:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # want positive (we are closer), reward smaller od and smaller myd
            val = (od - myd) * 2 - myd * 0.05 - od * 0.02
            if val > catch:
                catch = val

        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.004

        # If we cannot beat opponent on their nearest, switch to contesting any resource where we are gaining.
        switch_pen = 0.0
        if best_opp_res is not None:
            tx, ty = best_opp_res
            if man(nx, ny, tx, ty) > best_opp_d:
                switch_pen = 0.25

        val = on_res * 50 + race * 3.0 + catch * 1.2 + center - switch_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]