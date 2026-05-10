def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1, h - 1)
        if ((ox + oy) & 1) == 0:
            tx, ty = (0, 0)
        bestv, bestm = -10**18, [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - 0.001 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, bestm = v, [dx, dy]
        return bestm

    # Pre-scan resources sorted deterministically
    resources = sorted(resources)
    bestv, bestm = -10**18, [0, 0]

    # For each candidate next cell, choose the resource where we most outpace opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        best_for_cell = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Primary: maximize advantage (we're closer than opponent). Secondary: prefer nearer.
            # Small tie-break to keep deterministic motion preference.
            v = (do - ds) * 1000 - ds - 0.0001 * (abs(rx - nx) + abs(ry - ny))
            if v > best_for_cell:
                best_for_cell = v
        if best_for_cell > bestv:
            bestv, bestm = best_for_cell, [dx, dy]

    return bestm