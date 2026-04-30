def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in valid:
            sc = cheb(nx, ny, tx, ty)
            key = (sc, abs(nx - ox) + abs(ny - oy), nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    best_overall = None
    for x, y in res:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        adv = do - ds  # positive means we are closer or equal
        # prefer closer for both, and deterministic tie-break by coordinates
        key = (-adv, ds, do, x, y)
        if best_overall is None or key < best_overall[0]:
            best_overall = (key, x, y)
    _, tx, ty = best_overall

    best_move = None
    for dx, dy, nx, ny in valid:
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # also prevent stepping into "worse" positions vs resources by estimating next advantage
        step_adv = no - ns
        # small tie-break: favor not moving away from opponent (more denial)
        deny = cheb(nx, ny, ox, oy)
        key = (-step_adv, ns, -deny, nx, ny, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])
    return best_move[1]