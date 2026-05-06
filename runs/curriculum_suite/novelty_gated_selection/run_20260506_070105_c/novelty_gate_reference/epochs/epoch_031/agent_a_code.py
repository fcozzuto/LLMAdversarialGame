def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Pick a contest target where opponent is currently relatively disadvantaged.
    best_t = None
    best_adv = -10**9
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # positive => we are closer
        if adv > best_adv or (adv == best_adv and (sd, od, rx, ry) < (md(sx, sy, best_t[0], best_t[1]), md(ox, oy, best_t[0], best_t[1]), best_t[0], best_t[1]) if best_t else True):
            best_adv = adv
            best_t = (rx, ry)

    # If all are invalid, just move safely.
    if best_t is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    tx, ty = best_t
    cur_sd = md(sx, sy, tx, ty)
    cur_od = md(ox, oy, tx, ty)

    # One-step lookahead: maximize our progress while making it hard for opponent to reach the same target.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = md(nx, ny, tx, ty)
        nod = cur_od  # opponent hasn't moved; we infer deterrence by how far we pull away
        # Prefer moves that:
        # 1) reduce our distance to target
        # 2) increase the distance gap between opponent and us (target contest)
        # 3) keep us away from corners only if it worsens contest
        gap = nod - nsd
        # Mild tie-break: also consider grabbing nearest resource (greedy fallback)
        nearest_dist = 10**9
        for rx, ry in resources:
            if inb(rx, ry):
                d = md(nx, ny, rx, ry)
                if d < nearest_dist:
                    nearest_dist = d
        key = (-gap, nsd, nearest_dist, dx, dy, nx, ny)
        # We want larger gap => smaller -gap; also prefer smaller nsd
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]