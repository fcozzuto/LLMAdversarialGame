def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def pick_target():
        if not resources:
            return ((w - 1) // 2, (h - 1) // 2)
        best = None
        bx, by = 0, 0
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            my = md(sx, sy, rx, ry)
            op = md(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer than opponent.
            key = (my - op, my)
            if best is None or key < best:
                best = key
                bx, by = rx, ry
        return (bx, by)

    tx, ty = pick_target()

    bestv = None
    best = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        myd = md(nx, ny, tx, ty)
        opd = md(nx, ny, ox, oy)

        # Avoid getting too close to opponent (deterministic safety).
        close_pen = 0
        if opd <= 1:
            close_pen = 10 + 3 * (1 - opd)

        # Main objective: reduce our distance to target while increasing opponent distance to their own pressure.
        # Also slightly reward moving away from opponent along the direction of target competition.
        comp = md(nx, ny, tx, ty) - md(sx, sy, tx, ty)  # improvement sign
        v = (-(myd)) + 1.6 * (opd) - 0.9 * close_pen + (-0.2 * comp)

        # Tie-break deterministically by favoring smaller dx,dy order already in dirs;
        # then by smaller myd.
        if bestv is None or v > bestv or (v == bestv and myd < md(sx + best[0], sy + best[1], tx, ty)):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]