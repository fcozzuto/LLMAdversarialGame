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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def steps(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev distance

    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obs:
            continue
        my = steps(sx, sy, rx, ry)
        op = steps(ox, oy, rx, ry)
        # Prefer resources I can get strictly before; otherwise prefer ones with smallest my time.
        # Tie-break with parity to reduce oscillation.
        key = (0 if my < op else 1, my - op, my, (rx + ry) & 1, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    if best is None:
        # No valid resource: move toward opponent start corner midpoint-ish deterministically
        tx, ty = (w - 1, h - 1)
    else:
        tx, ty = best[1]

    best_step = None
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = steps(nx, ny, tx, ty)
        # If multiple, keep closer while avoiding giving opponent immediate access: prefer cells where opponent steps are not much better.
        opd = steps(ox, oy, tx, ty)
        val = (d, abs(opd - d), (nx + ny) & 1)
        if best_step is None or val < best_d:
            best_step = (dx, dy)
            best_d = val

    if best_step is None:
        return [0, 0]
    dx, dy = best_step
    return [int(dx), int(dy)]