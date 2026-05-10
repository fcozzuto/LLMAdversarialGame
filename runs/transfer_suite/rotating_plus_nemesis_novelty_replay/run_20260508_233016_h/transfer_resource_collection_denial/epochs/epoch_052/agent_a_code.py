def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target selection: prefer resources we are closer to, else deny/neutralize opponent lead.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = sd - od  # negative means we are closer
        # Slight anti-sweep heuristic: avoid long horizontal/vertical commitments when tied.
        spread = abs(rx - sx) + abs(ry - sy)
        if best is None:
            best = (lead, sd, od, spread, rx, ry)
        else:
            cand = (lead, sd, od, spread, rx, ry)
            if cand < best:
                best = cand
    tx, ty = best[4], best[5]

    # Move selection: evaluate next step, avoid obstacles, and maximize advantage.
    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Advantage-based score: maximize (opponent_d - my_d), then closeness to target.
        adv = opd - myd
        # Also discourage stepping that increases overall distance from any resource (keeps pressure).
        near_pen = 0
        for rx, ry in resources:
            near_pen += man(nx, ny, rx, ry) <= 2
        # Tie-break deterministically: prefer minimal distance to target, then "toward" tx/ty.
        toward = abs(nx - tx) + abs(ny - ty)
        cand = (-(adv), myd, toward, -near_pen, dx, dy)
        if best_score is None or cand < best_score:
            best_score = cand
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]