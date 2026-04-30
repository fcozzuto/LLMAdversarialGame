def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                val = abs(ox - nx) + abs(oy - ny)  # deterministic fallback: drift away
                if best is None or val > best[0]:
                    best = (val, [dx, dy])
        return best[1] if best else [0, 0]

    def dsq(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Choose a target resource where we are relatively closer than opponent.
    best_t = None
    for rx, ry in resources:
        d_self = dsq(sx, sy, rx, ry)
        d_opp = dsq(ox, oy, rx, ry)
        # Prefer: we are closer; tie-break: smaller our distance; then stable ordering.
        key = (-(d_opp - d_self), d_self, rx, ry)
        if best_t is None or key < best_t[0]:
            best_t = (key, (rx, ry))
    tx, ty = best_t[1]

    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my = dsq(nx, ny, tx, ty)
        # Counterplay: if opponent is closer to the target, try to move in a way that increases their distance.
        opd = dsq(ox, oy, tx, ty)
        opp_next_best = opd
        for odx, ody in moves:
            nnx, nny = ox + odx, oy + ody
            if inb(nnx, nny):
                opp_next_best = min(opp_next_best, dsq(nnx, nny, tx, ty))
        # Also discourage moving into being closer to opponent than us (keeps tension).
        opp_to_us = dsq(nx, ny, ox, oy)
        us_to_opp = dsq(sx, sy, ox, oy)
        val = (my, opp_next_best, opp_to_us, us_to_opp, dx, dy)
        if best_m is None or val < best_m[0]:
            best_m = (val, [dx, dy])

    return best_m[1] if best_m else [0, 0]