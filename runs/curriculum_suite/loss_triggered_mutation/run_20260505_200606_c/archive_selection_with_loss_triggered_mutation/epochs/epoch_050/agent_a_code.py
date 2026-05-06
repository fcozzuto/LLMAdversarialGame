def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(dx, dy) for dx, dy in moves if not (dx == 0 and dy == 0)]

    # If resources exist, race for the best one and avoid letting opponent get closer.
    if resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Key: maximize advantage; then prefer shorter distance to target; then keep farther from opponent.
            for rx, ry in resources:
                myd = md(nx, ny, rx, ry)
                opd = md(ox, oy, rx, ry)
                # Advantage first; if tie, minimize myd; if still tie, maximize separation from opponent.
                sep = md(nx, ny, ox, oy)
                key = (opd - myd, -myd, sep, -dx, -dy, rx, ry)
                if best is None or key > best[0]:
                    best = (key, dx, dy)
        if best is not None:
            return [int(best[1]), int(best[2])]

    # No visible resources: move toward center while drifting slightly away from opponent.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer smaller distance to center; if tie, prefer larger distance to opponent.
        dc = abs(nx - cx) + abs(ny - cy)
        dsep = md(nx, ny, ox, oy)
        key = (-dc, dsep, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)
    if best is not None:
        return [int(best[1]), int(best[2])]

    return [0, 0]