def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a resource: prefer being closer than opponent; otherwise pick the one with minimal opponent lead.
    best = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        lead = opd - myd  # positive is good
        # Bias: intercept near opponent sweep by prioritizing resources on/near opponent's current row.
        row_bias = 0
        if ry == oy:
            row_bias = 1
        elif abs(ry - oy) == 1:
            row_bias = 0.5
        if best is None:
            best = (lead + row_bias, -myd, rx, ry)
        else:
            cand = (lead + row_bias, -myd, rx, ry)
            if cand[:2] > best[:2]:
                best = cand
    tx, ty = best[2], best[3]

    # Choose neighbor: minimize my distance; also try to worsen opponent distance relative to me.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = man(nx, ny, tx, ty)
        opd2 = man(ox, oy, tx, ty)
        # opponent penalty if we reduce their ability: increase (myd2 - opd2) is bad, so minimize it
        score = (myd2 - opd2, myd2, abs(ny - oy), abs(nx - ox))
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move