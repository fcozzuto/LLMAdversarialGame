def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    if res:
        def best_value(nx, ny):
            dself = 10**9
            for rx, ry in res:
                d = md(nx, ny, rx, ry)
                if d < dself:
                    dself = d
            dop = md(nx, ny, ox, oy)
            return dself * 10 - dop
        best = None
        for dx, dy, nx, ny in moves:
            v = best_value(nx, ny)
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    # No resources visible: move toward center while keeping distance from opponent
    tx, ty = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy, nx, ny in moves:
        v = md(nx, ny, tx, ty) * 10 - md(nx, ny, ox, oy)
        if best is None or v < best[0]:
            best = (v, dx, dy)
    return [best[1], best[2]]