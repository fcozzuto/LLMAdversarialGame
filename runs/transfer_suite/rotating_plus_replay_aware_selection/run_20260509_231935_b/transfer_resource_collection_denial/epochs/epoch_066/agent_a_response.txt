def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    if not res:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def dist(a, b):
        # Chebyshev distance matches diagonal moves well
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_move = [0, 0]
    best_key = (-10**18, -10**18, -10**18)

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate best resource from this next position
        # Key: maximize distance advantage over opponent; then minimize own distance;
        # then prefer moving toward center (avoid cornering/stalling).
        local_best = (-10**18, 10**18, -10**18)
        for rx, ry in res:
            myd = dist((nx, ny), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            adv = opd - myd
            if (adv, -myd, (-(abs(nx - cx) + abs(ny - cy)))) > local_best:
                local_best = (adv, -myd, -(abs(nx - cx) + abs(ny - cy)))

        if local_best > best_key:
            best_key = local_best
            best_move = [dxm, dym]

    return best_move