def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    best_t = None
    best_key = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if not ok(x, y):
                continue
            sd = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            # Prefer resources where we are closer than opponent.
            key = (sd - od, sd, -od, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (x, y)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_mkey = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        dist_to_opp = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: keep advantage over opponent;
        # Tertiary: avoid being too close to opponent.
        mkey = (sd, sd - od, dist_to_opp * -1, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]