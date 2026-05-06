def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

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

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # deterministic "pressure": drift to reduce distance to opponent and toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            key = (md(nx, ny, ox, oy), md(nx, ny, cx, cy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Pick a contest target: prefer resources where we are closer (or can quickly get there) while
    # also keeping opponent farther from it.
    best_target = resources[0]
    best_val = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # smaller is better: we like (od - sd) negative/low and also prefer being closer overall
        val = (od - sd) * 10 + sd
        if best_val is None or val < best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target

    # Move scoring: prioritize reducing our distance to target and increasing opponent distance to that target.
    # Add mild tie-break to avoid standing still unless forced.
    best = None
    for dx, dy, nx, ny in moves:
        sd2 = md(nx, ny, tx, ty)
        od2 = md(ox, oy, tx, ty)
        # If we move toward the opponent, that's only good if it also improves our target progress.
        approach_opp = md(nx, ny, ox, oy)
        key = (sd2 * 3 - od2, sd2, approach_opp, dx == 0 and dy == 0, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]