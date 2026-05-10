def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not resources:
        return [0, 0]

    # Pick a deterministic target resource: maximize advantage (opp_d - my_d), then prefer closer, then toward center.
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for rx, ry in resources:
        if not valid(rx, ry):
            continue
        myd = abs(sx - rx) + abs(sy - ry)
        od = abs(ox - rx) + abs(oy - ry)
        adv = od - myd  # positive: we are closer
        center = -((rx - cx0) * (rx - cx0) + (ry - cy0) * (ry - cy0))
        key = (adv, -myd, center, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # Choose move that best improves our distance to target; tie-break by preserving advantage vs opponent.
    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = abs(nx - tx) + abs(ny - ty)
        od2 = abs(ox - tx) + abs(oy - ty)
        adv2 = od2 - myd2
        # Prefer immediate advantage, then closer to target, then keep away from edges deterministically.
        edge_bias = (nx - (w - 1) / 2.0) * (nx - (w - 1) / 2.0) + (ny - (h - 1) / 2.0) * (ny - (h - 1) / 2.0)
        key = (adv2, -myd2, -edge_bias, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]