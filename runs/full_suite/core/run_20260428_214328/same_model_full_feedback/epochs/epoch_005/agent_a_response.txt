def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def obs_pen(x, y):
        if (x, y) in obs:
            return 10**9
        if not obs:
            return 0
        md = 10**9
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        if md >= 4:
            return 0
        return (4 - md) * 7

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose target with strongest "beating opponent" advantage, then shortest my distance.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        center = - (abs(rx - cx) + abs(ry - cy))
        key = (adv, -myd, center, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    if best is None:
        dx, dy = 0, 0
        return [dx, dy]

    _, tx, ty = best
    # Move selection: best immediate estimate toward target, while improving advantage and avoiding obstacles.
    best_move = (10**18, -10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv_after = opd - myd
        score = myd + obs_pen(nx, ny)
        tie = -adv_after
        # Deterministic tie-break: prefer staying closer to center if still tied.
        center_tie = abs(nx - cx) + abs(ny - cy)
        cur = (score, tie, center_tie, dx * 10 + dy)
        if cur < best_move:
            best_move = cur
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]