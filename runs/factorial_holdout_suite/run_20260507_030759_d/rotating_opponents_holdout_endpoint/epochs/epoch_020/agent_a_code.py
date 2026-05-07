def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not (isinstance(sx, int) and isinstance(sy, int) and 0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, x, y):
        dx = abs(x - a)
        dy = abs(y - b)
        return dx if dx > dy else dy

    def best_target():
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = r[0], r[1]
            if not (isinstance(tx, int) and isinstance(ty, int) and inb(tx, ty)):
                continue
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = od - sd  # positive means we reach earlier
            key = (-adv, sd, tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        return best[1] if best else None

    target = best_target()
    if target is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in oset:
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_curr = cheb(sx, sy, tx, ty)
        progress = d_curr - d_to
        opp_threat = cheb(ox, oy, tx, ty)  # deterministic tie-break context
        key = (-progress, d_to, opp_threat, nx, ny)
        if key < best_move:
            best_move = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]