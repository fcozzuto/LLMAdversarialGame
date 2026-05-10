def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(obstacles)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    if not resources:
        tx = w - 1 if ox < w / 2 else 0
        ty = h - 1 if oy < h / 2 else 0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            key = (d, md(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best = key
        if best is None:
            return [0, 0]
        return [best[2], best[3]]

    best = None
    risk = 1 if observation.get("scores", [0, 0])[0] >= observation.get("scores", [0, 0])[1] else 2
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dmin = 10**9
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if d < dmin:
                dmin = d
        do = md(nx, ny, ox, oy)
        key = (dmin, -do * risk, dx, dy)
        if best is None or key < best:
            best = key
    if best is None:
        return [0, 0]
    return [best[2], best[3]]