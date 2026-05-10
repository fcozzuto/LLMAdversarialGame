def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_m(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score_cell(rx, ry):
        if not inb(rx, ry):
            return 10**9
        myd = dist_m(sx, sy, rx, ry)
        opd = dist_m(ox, oy, rx, ry)

        # vs sweep_rows: resources on opponent's current row/col are likely to be taken soon
        row_pen = 7 if ry == oy else 0
        col_pen = 3 if rx == ox else 0

        # stronger race bias: prefer where we are clearly closer
        race = myd - 1.35 * opd

        # slight tie-break to keep moving toward the center
        center = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        return race + row_pen + col_pen + 0.01 * center

    target = None
    best = None
    for rx, ry in resources:
        sc = score_cell(rx, ry)
        key = (sc, dist_m(sx, sy, rx, ry), rx + ry, rx, ry)
        if best is None or key < best:
            best = key
            target = (rx, ry)

    tx, ty = target
    dx_t = 0 if tx == sx else (1 if tx > sx else -1)
    dy_t = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            # move preference: closer to target, then reduce opponent access
            my_after = dist_m(nx, ny, tx, ty)
            race_after = my_after - 1.1 * dist_m(ox, oy, tx, ty)
            align = (abs(dx - dx_t) + abs(dy - dy_t)) * 0.01
            candidates.append(((race_after + my_after + align), dx, dy))

    if candidates:
        candidates.sort()
        _, dx, dy = candidates[0]
        return [int(dx), int(dy)]

    # fallback: stay or step if possible
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [int(dx), int(dy)]
    return [0, 0]