def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obs:
            continue
        my = dist(sx, sy, rx, ry)
        op = dist(ox, oy, rx, ry)
        # Prefer strictly earlier; then maximize (op - my); then closer; then stable tie-break by coordinate.
        key = (0 if my < op else 1, -(op - my), my, (rx * 3 + ry * 7) % 11, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_r

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dist(nx, ny, tx, ty)
        myd = dist(nx, ny, tx, ty)
        opd = dist(ox, oy, tx, ty)
        # Primary: minimize distance to target; Secondary: keep advantage; Tertiary: deterministic by direction.
        key = (nd, 0 if myd < opd else 1, -(opd - myd), (dx + 1) * 10 + (dy + 1))
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    # If all moves are blocked, stay (engine will keep us in place).
    return [int(best_move[0]), int(best_move[1])]