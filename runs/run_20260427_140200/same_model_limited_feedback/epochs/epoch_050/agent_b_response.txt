def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    res = observation.get("resources", [])

    obs = set((x, y) for x, y in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev for king moves

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            cands.append((nx, ny, dx, dy))

    if not res:
        # No resources: drift toward center while keeping some distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for nx, ny, dx, dy in cands:
            dcen = abs(nx - cx) + abs(ny - cy)
            dop = dist((nx, ny), (ox, oy))
            val = (dcen, -dop, abs(dx) + abs(dy))
            if best is None or val < best[0]:
                best = (val, [dx, dy])
        return best[1] if best else [0, 0]

    # Pick a deterministic target: we want a resource where we're relatively closer than opponent.
    best_resource = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obs:
            continue
        our_d = dist((sx, sy), (rx, ry))
        opp_d = dist((ox, oy), (rx, ry))
        key = (our_d - opp_d, our_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_resource = (rx, ry)

    tx, ty = best_resource
    best = None
    for nx, ny, dx, dy in cands:
        our_d = dist((nx, ny), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))
        # Prefer getting closer to target; break ties by moving to make opponent farther; prefer staying if equal.
        val = (our_d, abs(our_d - opp_d), -dist((nx, ny), (ox, oy)), abs(dx) + abs(dy), dx, dy)
        if best is None or val < best[0]:
            best = (val, [dx, dy])
    return best[1] if best else [0, 0]