def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    for dx0, dy0 in deltas:
        nx, ny = sx + dx0, sy + dy0
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_cell_val = -10**9
        best_cell_t = None
        for rx, ry in resources:
            myd = kdist(nx, ny, rx, ry)
            opd = kdist(ox, oy, rx, ry)

            # Penalize targets likely to be "swept" by opponent: same row (y) as opponent
            sweep_pen = 0
            if ry == oy:
                sweep_pen = 3 * (1 if abs(rx - ox) <= 1 else 0) + 1

            # Strong preference for winning the reach race; small preference for nearer cells
            val = (opd - myd) * 10 - myd - sweep_pen

            # Deterministic tie-break: lower myd, then lexicographic resource
            if val > best_cell_val:
                best_cell_val = val
                best_cell_t = (rx, ry, myd, opd)

        if best_cell_t is None:
            continue

        candidate = (best_cell_val, -best_cell_t[2], -best_cell_t[3], best_cell_t[0], best_cell_t[1], dx0, dy0)
        if best is None or candidate > best:
            best = candidate

    if best is None:
        return [0, 0]
    return [int(best[5]), int(best[6])]