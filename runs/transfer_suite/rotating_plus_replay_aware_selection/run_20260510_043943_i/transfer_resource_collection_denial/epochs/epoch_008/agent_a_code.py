def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid_cell(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # Pick a target resource that maximizes our advantage in arrival time.
    best_r = None
    best_adv = -10**9
    best_myd = 10**9
    for rx, ry in resources:
        if not valid_cell(rx, ry):
            continue
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        adv = opd - myd
        # Prefer secure wins first; then maximize advantage; break ties by shorter my distance.
        if adv > best_adv or (adv == best_adv and myd < best_myd):
            best_adv = adv
            best_myd = myd
            best_r = (rx, ry)

    if best_r is None:
        # No valid resource: move toward opponent to contest.
        tx, ty = ox, oy
    else:
        tx, ty = best_r

    # Choose a move that keeps/creates advantage toward the chosen target.
    best_score = None
    best_move = (0, 0)
    base_myd = man(sx, sy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid_cell(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Primary: maximize our arrival lead; secondary: minimize our remaining distance; tertiary: avoid staying.
        score = (opd - myd) * 100 - myd - (1 if (dx, dy) == (0, 0) else 0) - (0 if myd <= base_myd else 2)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]