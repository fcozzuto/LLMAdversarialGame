def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cells = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cells.append((dx, dy, nx, ny))
    if not cells:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target: resource where we are closest advantage; if none, take one closest to us.
    best = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        adv = opd - myd  # higher => we are closer or less behind
        cand = (adv, -myd, - (rx + 31 * ry))
        if best is None or cand > best[0]:
            best = (cand, (rx, ry))
    tx, ty = best[1]

    # Move selection: minimize our distance to target while maximizing relative advantage; avoid stepping away.
    best_move = None
    best_val = None
    my0 = man(sx, sy, tx, ty)
    opp0 = man(ox, oy, tx, ty)
    for dx, dy, nx, ny in cells:
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Opponent can move too; approximate by preferring states where we keep/extend advantage.
        rel = opd - myd
        dist_gain = my0 - myd  # positive is good
        tie = -(abs(nx - tx) + abs(ny - ty) + 0.01 * (dx * dx + dy * dy))
        val = (rel, dist_gain, tie, -(nx + 17 * ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]