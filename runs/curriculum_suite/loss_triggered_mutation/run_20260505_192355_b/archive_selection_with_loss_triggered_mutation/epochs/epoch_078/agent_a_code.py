def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not res:
        # drift toward center-ish while avoiding immediate obstacles
        cx, cy = w // 2, h // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = abs(nx - cx) + abs(ny - cy)
            key = (d, dx * 10 + dy, nx, ny)
            if key < best:
                best = key
        return [best[2] - sx, best[3] - sy] if best[2] != 0 or best[3] != 0 else [0, 0]

    # pick best resource by advantage; tie-break by nearer to us, then by lex cell
    best_cell = None
    best_key = None
    for cell in res:
        sd = dist((sx, sy), cell)
        od = dist((ox, oy), cell)
        adv = od - sd  # higher means we are closer
        key = (-adv, sd, cell[0], cell[1])  # minimize negative advantage => maximize adv
        if best_key is None or key < best_key:
            best_key = key
            best_cell = cell

    tx, ty = best_cell
    # evaluate one-step moves against the chosen target, with fallback if blocked
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd = abs(nx - tx) + abs(ny - ty)
        od = abs(ox - tx) + abs(oy - ty)
        adv = od - sd
        # prefer higher advantage, then shorter distance to target, then deterministic move order
        key = (-adv, sd, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is not None:
        return [best[1], best[2]]

    # absolute fallback: any legal move (deterministic lex by dx,dy order in moves list)
    for dx, dy in moves:
        if inb(sx + dx, sy + dy):
            return [dx, dy]
    return [0, 0]