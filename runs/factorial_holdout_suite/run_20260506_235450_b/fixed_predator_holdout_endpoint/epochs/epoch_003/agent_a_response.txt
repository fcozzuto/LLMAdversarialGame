def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            key = (-man(nx, ny, tx, ty), nx, ny)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_res = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources where we are relatively closer (or opponent is relatively farther)
        key = (do - ds, -ds, rx, ry)  # deterministic tie
        if best_res is None or key > best_res[0]:
            best_res = (key, (rx, ry))
    tx, ty = best_res[1]
    if sx == tx and sy == ty:
        return [0, 0]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = man(nx, ny, tx, ty)
        no = man(ox, oy, tx, ty)
        # After moving, favor reducing distance to target; if tied, favor increasing opponent's relative disadvantage
        rel = (no - ns)
        key = (-ns, -rel, dx, dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]] if best else [0, 0]