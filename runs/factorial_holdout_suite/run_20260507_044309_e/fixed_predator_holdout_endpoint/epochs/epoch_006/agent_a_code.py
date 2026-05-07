def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if not resources:
        # When nothing visible: go to the center to stay able to grab first revealed resources
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = None
        for dx, dy, nx, ny in candidates:
            # also avoid letting opponent get strictly closer to us
            self_d = abs(nx - ox) + abs(ny - oy)
            v = -((nx - cx) ** 2 + (ny - cy) ** 2) - 0.01 * self_d
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a target resource where we are closer than opponent (or closest to becoming so)
    best_r = None
    best_rv = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources where we can beat the opponent by a margin; slightly prefer closer ones
        rv = (od - sd) + 0.15 / (1 + sd)
        if best_rv is None or rv > best_rv:
            best_rv = rv
            best_r = (rx, ry)

    rx, ry = best_r
    base_sd = man(sx, sy, rx, ry)
    base_od = man(ox, oy, rx, ry)

    # Evaluate each move: maximize our advantage to the target, discourage moves that let opponent "overtake"
    best = None
    bestv = None
    for dx, dy, nx, ny in candidates:
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)  # opponent position assumed constant this step for heuristic
        adv = (od - sd)
        # Denial pressure: avoid steps that significantly reduce distance between opponent and us
        opp_to_us = man(ox, oy, nx, ny)
        us_to_opp_before = man(ox, oy, sx, sy)
        denial = opp_to_us - us_to_opp_before
        # Small tie-break: prefer not to move away from target
        approach = base_sd - sd
        v = adv + 0.5 * approach - 0.02 * denial
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]