def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles or not inb(rx, ry):
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; if close, prefer those closer to both (safer contention).
        key = (-(od - sd), sd, od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    if best_t is None:
        # No visible resources: drift to increase distance from opponent while staying valid.
        tx, ty = ox, oy
    else:
        tx, ty = best_t

    # If we are at/near a resource, consider switching to nearest competitive one.
    best = None
    best_move = (0, 0)
    res_positions = set(tuple(p) for p in resources)
    if (sx, sy) in res_positions:
        for rx, ry in resources:
            if (rx, ry) in obstacles or not inb(rx, ry):
                continue
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            key = (-(od - sd), sd, od, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        if best_t is not None:
            tx, ty = best_t

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # For denial: among equal progress, prefer moves that increase opponent's relative disadvantage.
        rel = opd - myd
        # Small penalty for moving away from current target.
        same_row_col = 1 if (tx == ox and ny == oy) or (tx == nx and ty == ny) else 0
        key = (-rel, myd, abs(nx - tx) + abs(ny - ty), opd, same_row_col, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]