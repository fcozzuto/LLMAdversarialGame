def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_xy(p):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                return (x, y)
        return None

    obs = set()
    for p in observation.get("obstacles", []) or []:
        t = to_xy(p)
        if t is not None:
            obs.add(t)

    res = []
    for p in observation.get("resources", []) or []:
        t = to_xy(p)
        if t is not None and t not in obs:
            res.append(t)

    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in res:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        key = (d1, -d2, rx + ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    def sign(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    want_dx = sign(tx - sx)
    want_dy = sign(ty - sy)

    moves = [
        (want_dx, want_dy), (want_dx, 0), (0, want_dy),
        (want_dx, -want_dy), (-want_dx, want_dy), (0, 0),
        (sign(tx - sx), sign(ty - sy)), (sign(tx - sx), 0), (0, sign(ty - sy))
    ]
    tried = set()
    bestm = None
    bestk = None

    for dx, dy in moves:
        if (dx, dy) in tried:
            continue
        tried.add((dx, dy))
        if dx < -1 or dx > 1 or dy < -1 or dy > 1:
            continue
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        key = (ds, -do, abs(dx) + abs(dy), dx, dy)
        if bestk is None or key < bestk:
            bestk = key
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]