def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    if not resources:
        return [0, 0]

    valid = []
    for p in resources:
        rx, ry = p[0], p[1]
        if inb(rx, ry) and (rx, ry) not in obstacles:
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    # Target selection: maximize how much closer we are than opponent (tie-break toward nearer/safer).
    best_t = None
    for rx, ry in valid:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        key = (-adv, sd, od, rx, ry)
        if best_t is None or key < best_t[0]:
            best_t = (key, (rx, ry))
    tx, ty = best_t[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Prefer getting closer to target; if we cannot, prefer reducing our distance to any resource where we can gain.
        if ns == 0:
            key = (-10, 0, 0, dx, dy)
        else:
            # Additional deterministic check: how we stand relative to opponent for the same target.
            adv2 = (cheb(ox, oy, tx, ty) - ns)
            key = (-adv2, ns, no, dx, dy)
        if best_m is None or key < best_m[0]:
            best_m = (key, [dx, dy])

    if best_m is None:
        return [0, 0]
    return best_m[1]