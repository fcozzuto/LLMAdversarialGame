def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [W - 1, H - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def ok(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    def dist_manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    # Choose a resource: prefer ones we can reach no worse than opponent; then closest to us; then closest to opponent (to avoid giving up).
    best = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        ds = dist_manh((sx, sy), (rx, ry))
        do = dist_manh((ox, oy), (rx, ry))
        # bucket: win/contest priority
        # (0 if ds<=do else 1). Then ds small. Then do small. Then deterministic tie by coords.
        key = (0 if ds <= do else 1, ds, do, rx, ry)
        if best is None or key < best:
            best = key

    # If no resources, head toward opponent-averaged corner target: deterministically move toward (max dist corner away from obstacles absent).
    if best is None:
        tx, ty = 0, 0
        # pick farthest corner from opponent
        candidates = [(0, 0), (0, H - 1), (W - 1, 0), (W - 1, H - 1)]
        bestcorner = None
        for c in candidates:
            d = dist_manh((ox, oy), c)
            if bestcorner is None or d > bestcorner[0] or (d == bestcorner[0] and c < bestcorner[1]):
                bestcorner = (d, c)
        tx, ty = bestcorner[1]
    else:
        tx, ty = best[3], best[4]

    # Evaluate moves greedily toward target, with small anti-worsen term vs opponent distance.
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds_next = dist_manh((nx, ny), (tx, ty))
        do_next = dist_manh((ox, oy), (tx, ty))
        # Prefer reduced distance to target; then avoid making opponent strictly closer to same target.
        key = (ds_next, 0 if dist_manh((ox, oy), (tx, ty)) >= ds_next else 1, ox - nx + oy - ny, dx, dy)
        # The third term ensures deterministic tie-break without needing randomness.
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]