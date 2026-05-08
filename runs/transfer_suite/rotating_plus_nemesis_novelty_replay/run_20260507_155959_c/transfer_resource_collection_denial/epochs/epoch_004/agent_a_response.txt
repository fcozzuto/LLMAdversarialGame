def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx + dy

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Pick a target resource we can reach first; otherwise pick best "threat" target by score margin heuristic.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # arrival priority: earlier first; then prefer tiles that are farther for opponent (denial pressure)
        key = (sd - od, sd, -od, rx, ry)
        # minimize key components lexicographically
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        # No resources visible: move to reduce distance to opponent's corner to intercept typical denial paths
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        best_d = None
        best = (0, 0)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = dist((nx, ny), (tx, ty))
            if best_d is None or d < best_d:
                best_d = d
                best = (dx, dy)
        return [best[0], best[1]]

    tx, ty = best_t
    # Greedy step toward target; if blocked, choose legal move that minimizes distance to target and tie-break deterministically.
    best_move = (0, 0)
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to = dist((nx, ny), (tx, ty))
        # Prefer progress; avoid getting too close to opponent when we can't secure target quickly
        d_op = dist((nx, ny), (ox, oy))
        # deterministic tie-break via dx,dy
        key = (d_to, -d_op, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]