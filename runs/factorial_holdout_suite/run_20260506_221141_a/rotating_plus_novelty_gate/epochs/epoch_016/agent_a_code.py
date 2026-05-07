def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set()
    for p in obstacles:
        if not p or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def cell_obstacle_risk(x, y):
        if not obs_set:
            return 0
        # Higher when closer to an obstacle.
        best = 10
        for (ox2, oy2) in obs_set:
            d = abs(x - ox2) + abs(y - oy2)
            if d < best:
                best = d
                if best == 0:
                    break
        return 9 - best if best <= 9 else 0

    best = None
    best_key = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not valid(tx, ty):
            continue
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd  # prefer arriving earlier or at same time
        # Key: primary advantage, then prefer smaller self distance, then prefer larger opponent distance
        key = (adv, -sd, od, -cell_obstacle_risk(tx, ty))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    deltas = [
        (0, 0),
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1),
    ]

    best_move = [0, 0]
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer moves reducing target distance; slight penalty for obstacle proximity.
        mkey = (-nd, -abs(nx - sx) - abs(ny - sy), -cell_obstacle_risk(nx, ny))
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    return best_move