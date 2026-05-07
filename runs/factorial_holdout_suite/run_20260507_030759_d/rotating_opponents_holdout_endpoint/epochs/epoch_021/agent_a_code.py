def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not (isinstance(sx, int) and isinstance(sy, int) and 0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = r[0], r[1]
        if not (isinstance(tx, int) and isinstance(ty, int) and inb(tx, ty)):
            continue
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd  # higher => we arrive no later
        key = (-adv, sd, tx, ty)
        if best is None or key < best[0]:
            best = (key, tx, ty)

    if best is None:
        return [0, 0]
    _, tx, ty = best

    def sgn(v):
        if v > 0: return 1
        if v < 0: return -1
        return 0

    dx0, dy0 = sgn(tx - sx), sgn(ty - sy)

    candidates = []
    order = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            candidates.append((cheb(nx, ny, tx, ty), -((dx == dx0) and (dy == dy0)), nx, ny))
    if not candidates:
        return [0, 0]

    candidates.sort()
    _, _, nx, ny = candidates[0]
    return [nx - sx, ny - sy]