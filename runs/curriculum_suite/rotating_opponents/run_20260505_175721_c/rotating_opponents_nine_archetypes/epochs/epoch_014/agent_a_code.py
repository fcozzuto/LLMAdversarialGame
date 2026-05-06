def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        try:
            x, y = p
            obst.add((int(x), int(y)))
        except Exception:
            pass

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        try:
            x, y = p
            res.append((int(x), int(y)))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obst

    def cheb(x1, y1, x2, y2):
        ax, ay = abs(x2 - x1), abs(y2 - y1)
        return ax if ax > ay else ay

    tx, ty = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if res:
            best_res = None
            for rx, ry in res:
                d = cheb(nx, ny, rx, ry)
                if best_res is None or d < best_res:
                    best_res = d
            ourd = best_res if best_res is not None else cheb(nx, ny, tx, ty)
            oppd = cheb(nx, ny, ox, oy)
            score = (1000 - ourd) - 2 * oppd
        else:
            ourd = cheb(nx, ny, tx, ty)
            score = (1000 - ourd) - cheb(nx, ny, ox, oy)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]