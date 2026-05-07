def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = list(observation.get("resources", []) or [])
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(x1, y1, x2, y2):
        a = x2 - x1
        b = y2 - y1
        if a < 0: a = -a
        if b < 0: b = -b
        return a if a > b else b

    if resources:
        best = None
        for r in resources:
            rx, ry = r[0], r[1]
            score = (cd(sx, sy, rx, ry) - cd(ox, oy, rx, ry), cd(sx, sy, rx, ry), rx, ry)
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    curd = cd(sx, sy, tx, ty)
    best_move = (0, 0)
    best_val = (10**9, 10**9, 10**9)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cd(nx, ny, tx, ty)
        oppd = cd(nx, ny, ox, oy)
        # Prefer smaller distance to target; break ties by (not moving toward opponent); then by direction deterministically
        val = (nd, -oppd, dx, dy)
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]