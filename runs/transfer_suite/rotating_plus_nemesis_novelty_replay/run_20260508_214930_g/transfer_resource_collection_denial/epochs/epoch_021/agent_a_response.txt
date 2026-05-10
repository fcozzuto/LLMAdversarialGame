def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2
    best = None
    tx = ty = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner (oppd-myd), then closer to us, then central.
        key = (oppd - myd, -myd, -cheb(rx, ry, cx, cy), -(rx * 9 + ry))
        if best is None or key > best:
            best = key
            tx, ty = rx, ry

    if tx is None:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_d = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        penalty = 1000 if (nx, ny) in obs else 0
        myd_after = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        adv = oppd - myd_after
        key = (adv, -myd_after, -penalty, -(dx * dx + dy * dy))
        if best_m is None or key > best_m:
            best_m = key
            best_d = [dx, dy]

    return best_d