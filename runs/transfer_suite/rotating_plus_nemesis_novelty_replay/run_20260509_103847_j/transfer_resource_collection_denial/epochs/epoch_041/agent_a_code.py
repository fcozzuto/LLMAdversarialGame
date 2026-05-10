def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_resource_for(px, py):
        # maximize (opp_like - self_like) where opp_like is distance to opponent position from the cell
        # => prefer resources closer to us than to opponent, but still contest via tie-breaks
        best = None
        for rx, ry in resources:
            ds = man(px, py, rx, ry)
            do = man(ox, oy, rx, ry)
            key = (do - ds, -ds, rx, ry)  # prefer larger advantage, then closer
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[1]

    def greedy_next(px, py):
        tx, ty = best_resource_for(px, py)
        bestm = (10**9, 10**9, 0, 0)
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, tx, ty)
            # minimize distance to its greedy target
            key = (d, man(nx, ny, sx, sy), dx, dy)
            if key < bestm:
                bestm = key
        dx, dy = bestm[2], bestm[3]
        if bestm[0] == 10**9:
            return [0, 0]
        return [dx, dy]

    # Predict opponent's next move using same local greedy heuristic
    odx, ody = greedy_next(ox, oy)
    nox, noy = ox + odx, oy + ody
    if not inb(nox, noy) or (nox, noy) in obstacles:
        nox, noy = ox, oy

    # Choose a target that we are relatively closer to, otherwise contest the best
    tx, ty = best_resource_for(sx, sy)

    best = None
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Progress towards our target
        d_self = man(nx, ny, tx, ty)
        d_opp = man(nox, noy, tx, ty)

        # Prefer moves that reduce our distance more than they reduce theirs,
        # and avoid being too close to opponent (so we don't get outcompeted next step).
        # Tie-break deterministically by closer distance to target then safer distance from opponent.
        opp_sep = man(nx, ny, nox, noy)
        key = (-(d_opp - d_self), d_self, -opp_sep, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]