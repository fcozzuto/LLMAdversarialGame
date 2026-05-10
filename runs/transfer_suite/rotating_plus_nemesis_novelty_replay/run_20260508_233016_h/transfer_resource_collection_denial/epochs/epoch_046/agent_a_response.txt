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

    # Pick resource we can "win first"; if none, pick one that minimizes opponent lead.
    best = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer winning (myd < opd), else minimize opponent advantage.
        if myd < opd:
            key = (0, myd, opd, rx, ry)
        elif myd == opd:
            key = (1, 0, myd, rx, ry)  # tie: smaller distance is better
        else:
            key = (2, opd - myd, myd, -opd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Score each move: move closer to target; if opponent closer too, reduce their advantage.
    best_mv = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_to = man(nx, ny, tx, ty)
        opp_to = man(ox, oy, tx, ty)
        # If target already adjacent/at, prefer collecting immediately.
        on_target = 1 if (nx, ny) == (tx, ty) else 0
        # Also consider nearest resource to keep flexibility if target becomes contested.
        best_other = None
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if best_other is None or d < best_other:
                best_other = d
        # Higher is better.
        score = (on_target * 1000) + (-my_to * 10) + ((opp_to - my_to) * 6) + (-best_other)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_mv):
            best_score = score
            best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]]