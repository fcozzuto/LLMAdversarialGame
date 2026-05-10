def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b  # Chebyshev (diagonal allowed)

    if not resources:
        return [0, 0]

    # Pick a target we can contest: maximize (opp_dist - my_dist), tie-break by closeness.
    best = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        if best is None:
            best = (opd - myd, -myd, -(rx + ry), rx, ry)
        else:
            key = (opd - myd, -myd, -(rx + ry), rx, ry)
            if key > best:
                best = key
    _, _, _, tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    myd0 = cd(sx, sy, tx, ty)
    opd0 = cd(ox, oy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = cd(nx, ny, tx, ty)

        # If we take a move, estimate whether we still beat the opponent on the target.
        # Also steer slightly to the target side if equal.
        est = (opd0 - myd) - (myd - myd0) * 0.25

        # Small repulsion from obstacles near the step.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1
        est -= adj_obs * 0.35

        # Prefer moves that progress in at least one coordinate toward target.
        prog = 0
        if (tx > sx and nx > sx) or (tx < sx and nx < sx) or tx == sx:
            prog += 1
        if (ty > sy and ny > sy) or (ty < sy and ny < sy) or ty == sy:
            prog += 1
        est += prog * 0.05

        # Tie-break deterministically: fixed ordering already, but compare with score.
        if best_score is None or est > best_score:
            best_score = est
            best_move = [dx, dy]

    return best_move