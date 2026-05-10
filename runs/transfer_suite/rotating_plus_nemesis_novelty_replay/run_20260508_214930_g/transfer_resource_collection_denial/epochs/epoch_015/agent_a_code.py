def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_key = None
    tx = ty = None
    cx, cy = w // 2, h // 2
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        win = oppd - myd
        center = cheb(rx, ry, cx, cy)
        key = (win, -myd, -center, -(rx * 9 + ry))
        if best_key is None or key > best_key:
            best_key = key
            tx, ty = rx, ry

    if tx is None:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        oppd2 = cheb(ox, oy, tx, ty)
        win2 = oppd2 - myd2
        # Prefer maximizing race advantage; then being closer; then moving toward center; finally deterministic tie.
        center2 = cheb(nx, ny, cx, cy)
        step_pen = (abs(dx) + abs(dy))
        key = (win2, -myd2, -center2, -step_pen, dx, dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    _, dx, dy = best
    return [int(dx), int(dy)]