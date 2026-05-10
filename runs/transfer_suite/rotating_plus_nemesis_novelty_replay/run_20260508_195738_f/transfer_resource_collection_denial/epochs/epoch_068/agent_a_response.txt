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
        tx, ty = w - 1, h - 1
        if (ox + oy) % 2 == 0:
            tx, ty = 0, 0
        bestv, bestm = -10**9, [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - 0.001 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, bestm = v, [dx, dy]
        return bestm

    resources = sorted(resources)
    bestm = [0, 0]
    bestv = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer states where we beat the opponent on some resource this turn (one-step lookahead).
        # Value: maximum (opp_dist - my_dist); tie-break toward smaller my_dist, then toward being nearer to opponent (denial).
        local_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            v = (opd - myd) * 1000 - myd * 2 - cheb(nx, ny, ox, oy) * 0.001
            if v > local_best:
                local_best = v
        # Ensure deterministic preference ordering even if local_best ties exactly.
        if local_best > bestv:
            bestv, bestm = local_best, [dx, dy]
    return bestm