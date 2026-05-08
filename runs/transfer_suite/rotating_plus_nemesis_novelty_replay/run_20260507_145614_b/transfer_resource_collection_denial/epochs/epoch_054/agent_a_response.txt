def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if inb(nx, ny) else [0, 0]

    for r in resources:
        if (sx, sy) == (r[0], r[1]):
            return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x2 - x1
        if ax < 0:
            ax = -ax
        ay = y2 - y1
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer (approx)
        # Prefer resources we can reach first, but also keep progress when not.
        key = (lead, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # Choose move that maximizes (lead after move), then minimizes our distance.
    best_move = (0, 0)
    best_tie = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = cheb(nx, ny, rx, ry)
        nod = cheb(ox, oy, rx, ry)
        key = (nod - nsd, -nsd)
        if best_tie is None or key > best_tie:
            best_tie = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]