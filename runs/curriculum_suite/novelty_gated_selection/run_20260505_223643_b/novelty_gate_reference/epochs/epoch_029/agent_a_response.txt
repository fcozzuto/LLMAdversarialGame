def choose_move(observation):
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is not None:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    candidates = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    if not resources:
        # Deterministic safe drift: increase cheb distance from opponent, avoid obstacles
        bestv = None
        best = (0, 0)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = (cheb(nx, ny, ox, oy), -abs(nx - (w - 1) // 2), -abs(ny - (h - 1) // 2))
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Pick a target where we are not clearly behind; otherwise pick the one we can swing toward.
    best_target = None
    best_t = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        s = cheb(sx, sy, rx, ry)
        o = cheb(ox, oy, rx, ry)
        ahead = o - s  # positive means we can arrive no later than opponent (tie gives 0)
        # Prefer positive ahead; then shorter our distance; then deterministic tie-break by coord
        t = (ahead, -s, -rx, -ry)
        if best_t is None or t > best_t:
            best_t = t
            best_target = (rx, ry)

    rx, ry = best_target
    # For each move, minimize our distance to target while maximizing opponent distance to target.
    bestv = None
    best = (0, 0)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)  # opponent position doesn't change this turn; still bias movement
        # Our progress is primary; small bonus for increasing relative gap to opponent
        v = (-myd, (opd - myd), -abs(nx - sx) - abs(ny - sy), -abs(nx - (w - 1) // 2), -abs(ny - (h - 1) // 2))
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]