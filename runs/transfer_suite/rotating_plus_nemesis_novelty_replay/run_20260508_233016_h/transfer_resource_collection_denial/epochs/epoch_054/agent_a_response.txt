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

    best_target = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer resources we can secure sooner; else deny by maximizing (opd - myd).
        # Also slight preference for closer overall to reduce drift.
        score = (0 if myd <= opd else 1, -(opd - myd), myd, rx, ry)
        if best_target is None or score < best_target[0]:
            best_target = (score, (rx, ry))
    tx, ty = best_target[1]

    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd_new = man(nx, ny, tx, ty)
        opd_new = man(ox, oy, tx, ty)
        adv = (opd_new - myd_new)  # higher is better (opponent farther relative)
        # If we are already behind badly, prioritize moves that improve advantage most.
        behind = (man(sx, sy, tx, ty) - man(ox, oy, tx, ty))
        primary = -adv if behind > 0 else -adv
        # Tie-break by reducing distance to target and then keeping movement small.
        dist = myd_new
        move_mag = abs(dx) + abs(dy)
        cand = (primary, dist, move_mag, dx, dy)
        if best_move is None or cand < best_move[0]:
            best_move = (cand, [dx, dy])

    return best_move[1] if best_move is not None else [0, 0]