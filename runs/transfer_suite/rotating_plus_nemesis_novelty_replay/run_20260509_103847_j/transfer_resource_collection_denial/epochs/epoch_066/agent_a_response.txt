def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obst = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_opp_step(px, py, tx, ty):
        best = None
        best_d = 10**9
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
                best = (dx, dy)
        if best is None:
            return (0, 0)
        return best

    if not resources:
        return [0, 0]

    # Choose a target deterministically that we are likely to reach not later than opponent.
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources where ds <= do, then tighten the margin; otherwise deny nearest-to-opponent.
        if ds <= do:
            key = (0, ds, do - ds, rx, ry)
        else:
            key = (1, do - ds, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # One-step lookahead against opponent greedy movement to the same target.
    o_dx, o_dy = best_opp_step(ox, oy, tx, ty)
    nox, noy = ox + o_dx, oy + o_dy
    opp_dist = man(nox, noy, tx, ty)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nsx, nsy = sx + dx, sy + dy
        if not inb(nsx, nsy):
            continue
        if (nsx, nsy) in obst:
            continue
        self_dist = man(nsx, nsy, tx, ty)
        # Higher score is better: win the race to target, then reduce distance; small preference to avoid wasting steps.
        score = (opp_dist - self_dist) * 1000 - self_dist
        if (nsx, nsy) == (tx, ty):
            score += 10**6
        # Deterministic tie-break: prefer earlier deltas order by comparing dx,dy lexicographically with a slight bias.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]