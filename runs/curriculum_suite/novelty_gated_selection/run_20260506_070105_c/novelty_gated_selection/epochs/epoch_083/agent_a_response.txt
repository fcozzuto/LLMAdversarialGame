def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            key = (man(nx, ny, tx, ty), -man(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [int(best[1]), int(best[2])] if best else [0, 0]

    # Choose a "most stealable" resource: small my_dist, large opp_dist.
    best_r = None
    for rx, ry in resources:
        dme = man(sx, sy, rx, ry)
        dop = man(ox, oy, rx, ry)
        # Prefer resources where we can potentially arrive earlier by margin.
        key = (-(dop - dme), dme, rx, ry)
        if best_r is None or key < best_r[0]:
            best_r = (key, rx, ry)
    _, tr_x, tr_y = best_r

    # If the opponent is very near, shift to defensive kiting while still moving toward target.
    opp_near = man(sx, sy, ox, oy) <= 2
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        myd = man(nx, ny, tr_x, tr_y)
        opd = man(nx, ny, ox, oy)

        # Main objective: reduce my distance to target while increasing distance from opponent.
        # Secondary: maximize advantage in reaching target.
        my_to_target = myd
        opp_to_target_after = man(ox, oy, tr_x, tr_y)
        advantage = (opp_to_target_after - myd)  # higher means closer than opponent (or less behind)

        if opp_near:
            # Kite: strong penalty for getting closer; still prefer target progress.
            key = (myd, opd * -2, -(advantage), dx, dy)
        else:
            key = (myd, -opd, -advantage, dx, dy)

        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])] if best else [0, 0]