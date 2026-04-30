def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    occ = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                occ.add((px, py))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in occ:
                resources.append((rx, ry))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources we reach sooner than opponent; small penalty for being far.
            score = (ds - 0.85 * do) * 1000 + ds
            if best is None or score < best:
                best = score
                target = (rx, ry)
    if target is None:
        # No visible resources: move to improve distance from opponent and not worsen position too much.
        best = None
        pick = (0, 0)
        for dx, dy, nx, ny in legal:
            score = man(nx, ny, ox, oy) * 10 + (nx + ny) * 0.01
            if best is None or score > best:
                best = score
                pick = (dx, dy)
        return [int(pick[0]), int(pick[1])]

    tx, ty = target
    # Avoid stepping into squares that let opponent be adjacent next step (softly).
    opp_adj = set()
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            if ddx == 0 and ddy == 0:
                continue
            ax, ay = ox + ddx, oy + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in occ:
                opp_adj.add((ax, ay))

    best = None
    pick = (0, 0)
    for dx, dy, nx, ny in legal:
        ds2 = man(nx, ny, tx, ty)
        dist_opp = man(nx, ny, ox, oy)
        block_pen = 50 if (nx, ny) in opp_adj else 0
        # Tie-break deterministically to reduce oscillation: prefer smaller dx, then smaller dy.
        score = ds2 * 10000 - dist_opp * 10 + block_pen + (dx + 1) * 3 + (dy + 1)
        if best is None or score < best:
            best = score
            pick = (dx, dy)

    return [int(pick[0]), int(pick[1])]