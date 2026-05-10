def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    tx = int(observation.get("turn_index", 0))

    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        a = ax - bx
        if a < 0: a = -a
        b = ay - by
        if b < 0: b = -b
        return a if a > b else b

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    best = None
    best_key = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        slack = do - ds
        # Prefer resources we can reach strictly earlier; otherwise reduce opponent lead.
        # Deterministic tie-break by parity and slight preference for being closer to the board corner.
        parity = (rx + ry + tx) & 1
        corner = (rx == (w - 1) or rx == 0) + (ry == (h - 1) or ry == 0)
        key = (-(1 if slack > 0 else 0), -slack, ds, parity, -corner)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # Try primary step; if invalid, choose best alternative deterministically.
    primary = (sx + dx, sy + dy)
    if valid(primary[0], primary[1]):
        return [dx, dy]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    scored = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        nds = cheb(nx, ny, rx, ry)
        ndo = cheb(ox, oy, rx, ry)
        slack = ndo - nds
        parity = (nx + ny + tx) & 1
        corner = (nx == (w - 1) or nx == 0) + (ny == (h - 1) or ny == 0)
        scored.append((( -(1 if slack > 0 else 0), -slack, nds, parity, -corner ), mx, my))
    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: t[0])
    return [int(scored[0][1]), int(scored[0][2])]