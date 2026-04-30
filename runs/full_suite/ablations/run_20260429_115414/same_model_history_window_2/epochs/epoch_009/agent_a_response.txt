def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    viable = []
    for r in resources:
        rx, ry = r[0], r[1]
        if legal(rx, ry):
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer targets where we arrive much earlier; then earlier (smaller myd); then tie-breakers stable.
            viable.append((rx, ry, od - myd, myd, abs((rx + ry) - (sx + sy)), -rx, -ry))
    tgt = None
    if viable:
        viable.sort(key=lambda t: (-t[2], t[3], t[4], t[5], t[6]))
        tgt = (viable[0][0], viable[0][1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if tgt is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = tgt

    # If target is directly blocked, aim for a nearby unblocked point deterministically.
    if not legal(tx, ty):
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = tx + dx, ty + dy
                if legal(nx, ny):
                    key = (cheb(ox, oy, nx, ny) - cheb(sx, sy, nx, ny), cheb(sx, sy, nx, ny), abs((nx + ny) - (sx + sy)), nx, ny)
                    if best is None or key < best[0]:
                        best = (key, nx, ny)
        if best is not None:
            tx, ty = best[1], best[2]
        else:
            tx, ty = w // 2, h // 2

    # Choose best single-step move toward target, while preventing stepping into obstacles.
    best_mv = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Main: move to reduce our distance; Secondary: keep opponent farther; Tertiary: avoid getting closer to them.
        myd = cheb(nx, ny, tx, ty)
        od_to_target = cheb(ox, oy, tx, ty)
        my_adv = (od_to_target - myd)
        # If equal, prefer smaller distance to target and smaller distance from opponent (keep stable tie-breakers).
        key = (-my_adv, myd, cheb(nx, ny, ox, oy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_mv = (dx, dy)
    return [best_mv[0], best_mv[1]]