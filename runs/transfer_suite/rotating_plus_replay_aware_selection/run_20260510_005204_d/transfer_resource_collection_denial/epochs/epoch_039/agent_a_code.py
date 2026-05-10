def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    cx0 = (w - 1) / 2.0
    cy0 = (h - 1) / 2.0

    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        center = -(abs(rx - cx0) + abs(ry - cy0))
        secure = 1 if myd <= opd else 0
        # Prefer resources where we're not worse, and maximize advantage; break ties with closeness.
        key = (secure, (opd - myd) * 5 - myd, center, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        center = -(abs(nx - cx0) + abs(ny - cy0))
        # Look one step: keep maximizing advantage while not drifting away.
        secure2 = 1 if myd2 <= opd2 else 0
        val = (secure2, (opd2 - myd2) * 5 - myd2, center, -(nx + ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move