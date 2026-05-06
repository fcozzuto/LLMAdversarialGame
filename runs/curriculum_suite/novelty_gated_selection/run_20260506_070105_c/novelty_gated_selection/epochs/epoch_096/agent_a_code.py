def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    def best_dir(target):
        tx, ty = target
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (dist(nx, ny, tx, ty), dist(nx, ny, ox, oy), -(abs(tx - ox) + abs(ty - oy)))
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return best

    if resources:
        nearest = None
        bestd = None
        for r in resources:
            d = dist(sx, sy, r[0], r[1])
            if bestd is None or d < bestd or (d == bestd and (r[0], r[1]) < nearest):
                bestd = d
                nearest = r
        move = best_dir(nearest)
        if move is not None:
            return [move[0], move[1]]

    # Fallback: move away from opponent if close, else toward center-ish
    dxo = sx - ox
    if dxo < 0:
        dxo = -dxo
    dyo = sy - oy
    if dyo < 0:
        dyo = -dyo
    too_close = dist(sx, sy, ox, oy) <= 2

    if too_close:
        # choose move that maximizes distance to opponent
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = dist(nx, ny, ox, oy)
            if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # toward interior (avoid edges) deterministically
    cx, cy = w // 2, h // 2
    move = best_dir((cx, cy))
    return [move[0], move[1]] if move is not None else [0, 0]