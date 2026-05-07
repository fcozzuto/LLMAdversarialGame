def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    best = None
    best_sc = None
    for p in resources:
        if not p or len(p) < 2:
            continue
        rx, ry = int(p[0]), int(p[1])
        if (rx, ry) in obs or not inb(rx, ry):
            continue
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # If we can arrive earlier, strongly prefer; otherwise prefer places where opponent is slower and we at least can contest.
        if myd < opd:
            sc = 100000 + (opd - myd) * 500 - myd
        elif myd == opd:
            sc = 90000 + 2000 - opd
        else:
            sc = (opd - myd) * 200 - myd * 5
        # Deterministic tie-breakers: prefer nearer, then lexicographically smaller.
        sc += -rx * 0.01 - ry * 0.001
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx, dy = sign(tx - sx), sign(ty - sy)

    # If direct step lands on an obstacle, try alternative axes deterministically.
    nx, ny = sx + dx, sy + dy
    if not inb(nx, ny) or (nx, ny) in obs:
        candidates = [(dx, 0), (0, dy), (sign(tx - sx), sign(ty - sy)), (0, 0)]
        for cdx, cdy in candidates:
            nx, ny = sx + cdx, sy + cdy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [cdx, cdy]
        return [0, 0]

    return [dx, dy]