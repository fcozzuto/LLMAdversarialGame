def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role)

    if pursuer:
        dx0 = 0 if ox == sx else (1 if ox > sx else -1)
        dy0 = 0 if oy == sy else (1 if oy > sy else -1)
        px, py = ox + dx0, oy + dy0
        if not ok(px, py):
            px, py = ox, oy
        tx, ty = px, py

        best = None
        bestd = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if bestd is None or d < bestd:
                bestd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best is not None else [0, 0]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    cx, cy = far_corner

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        to_corner = abs(nx - cx) + abs(ny - cy)
        block_adj = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if inb(ax, ay) and (ax, ay) in obstacles:
                    block_adj += 1
        v = dist * 100 - to_corner * 2 - block_adj
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])] if best is not None else [0, 0]