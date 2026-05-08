def choose_move(observation):
    w = observation.get("grid_width", 0) or 8
    h = observation.get("grid_height", 0) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    nbrs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                nbrs.append((dx, dy, nx, ny))
    if not nbrs:
        return [0, 0]

    if resources:
        # Prefer resources where we can arrive earlier than opponent (tie-break near our pos)
        best_cell = None
        best_key = None
        for tx, ty in resources:
            myd = man(sx, sy, tx, ty)
            opd = man(ox, oy, tx, ty)
            key = (myd - opd, myd, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best_cell = (tx, ty)
        tx, ty = best_cell

        # Choose among legal next moves: minimize remaining distance to target, then maximize opponent lag
        best = None
        best_key2 = None
        for dx, dy, nx, ny in nbrs:
            myd = man(nx, ny, tx, ty)
            opd = man(nx, ny, ox, oy)  # proxy: keep pressure / reduce exposure
            # Opponent arrival estimate to target from their current position
            oppd_to_target = man(ox, oy, tx, ty)
            # Favor steps that keep us closer to target than opponent already is
            adv = (myd - oppd_to_target)
            key2 = (adv, myd, -opd, dx, dy)
            if best_key2 is None or key2 < best_key2:
                best_key2 = key2
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No visible resources: drift away from opponent while heading to center
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for dx, dy, nx, ny in nbrs:
        dist_op = man(nx, ny, ox, oy)
        dist_ctr = man(nx, ny, cx, cy)
        key = (-dist_op, dist_ctr, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]