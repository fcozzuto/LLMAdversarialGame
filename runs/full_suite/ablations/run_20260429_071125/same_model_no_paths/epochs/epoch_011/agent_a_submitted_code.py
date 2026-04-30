def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not inside(sx, sy):
        for dx, dy in moves:
            if inside(sx + dx, sy + dy):
                sx, sy = sx + dx, sy + dy
                break

    def man(ax, ay, bx, by):
        d = ax - bx
        e = ay - by
        if d < 0: d = -d
        if e < 0: e = -e
        return d + e

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if resources:
            nearest = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < nearest:
                    nearest = d
            val = nearest * 10 - min(manh(nx, ny, ox, oy), 12)
        else:
            val = -man(nx, ny, ox, oy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            if inside(sx + dx, sy + dy):
                best = (dx, dy)
                break
    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]