def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        resources = [[w - 1, h - 1]]

    # Choose target resource: maximize advantage (opp distance - self distance), then closer to self, then farther from opp.
    best_r = None
    best_key = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd, od, -rx - ry, rx)
        if best_key is None or key > best_key:
            best_key, best_r = key, (rx, ry)
    tx, ty = best_r

    # Greedy one-step: maximize expected advantage after move; avoid obstacles; tie-break towards resource.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_m_key = None
    cur_sd = cheb(sx, sy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        adv = cheb(ox, oy, tx, ty) - nd
        # Prefer improving self distance; penalize moves that don't get closer (when not necessary).
        improve = cur_sd - nd
        key = (adv, improve, -nd, -(dx * dx + dy * dy), -abs(nx - tx) - abs(ny - ty))
        if best_m_key is None or key > best_m_key:
            best_m_key, best_m = key, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]