def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer than opponent; add small preference for being close.
            key = (od - sd, -sd)
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate: closest to target; avoid letting opponent benefit (increase our distance advantage).
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Also discourage stepping to far corners when already no resources.
        corner_pen = 0
        if not resources:
            corner_pen = (nx < 2 or nx > w - 3 or ny < 2 or ny > h - 3) * 2
        key = (-d_to_o, -corner_pen, -d_to_t, dx, dy)
        candidates.append((key, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True, key=lambda x: x[0])
    return candidates[0][1]