def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def move_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) == (sx, sy) or (rx, ry) in obs or not inb(rx, ry):
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we can reach no later; then closer; then further from opponent; then stable ordering
        key = (sd <= od, -(sd), -(max(0, sd - od)), -(abs(rx - ox) + abs(ry - oy)), -(rx + 7 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # Deterministic fallback: drift away from opponent while staying safe
        candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best_delta = [0, 0]
        best_val = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = (man(nx, ny, ox, oy), -man(nx, ny, sx, sy))
            if best_val is None or val > best_val:
                best_val = val
                best_delta = [dx, dy]
        return best_delta

    dx, dy = move_toward(best[0], best[1])
    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]

    # Obstacle avoidance: try moves in deterministic preference toward target, then stay
    tx, ty = best[0], best[1]
    prefs = []
    for ndx in (-1, 0, 1):
        for ndy in (-1, 0, 1):
            if ndx == 0 and ndy == 0:
                continue
            nmx, nmy = sx + ndx, sy + ndy
            if not valid(nmx, nmy):
                continue
            prefs.append((man(nmx, nmy, tx, ty), abs(ndx), abs(ndy), ndx, ndy))
    prefs.sort(key=lambda z: (z[0], -z[1] - z[2], z[3], z[4]))
    if prefs:
        return [prefs[0][3], prefs[0][4]]
    return [0, 0]