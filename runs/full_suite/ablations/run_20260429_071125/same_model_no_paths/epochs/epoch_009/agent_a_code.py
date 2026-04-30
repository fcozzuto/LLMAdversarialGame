def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not inb(sx, sy) or (sx, sy) in blocked:
        sx, sy = 0, 0

    target = None
    if resources:
        best_key = None
        for tx, ty in resources:
            ds = man(sx, sy, tx, ty)
            do = man(ox, oy, tx, ty)
            # prefer resources we can reach sooner; tie-break by closer
            key = (ds - do, -ds)
            if best_key is None or key < best_key:
                best_key = key
                target = (tx, ty)

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if target is not None:
        tx, ty = target
        best = None
        for dx, dy, nx, ny in legal:
            score = (man(nx, ny, tx, ty), man(nx, ny, ox, oy))
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])]

    # fallback: maximize distance from opponent
    best = None
    for dx, dy, nx, ny in legal:
        score = (-man(nx, ny, ox, oy), man(nx, ny, sx, sy))
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]