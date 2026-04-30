def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        # No resources: drift toward center while keeping away from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = [0, 0]
        bestv = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                d_center = abs(nx - cx) + abs(ny - cy)
                d_opp = abs(nx - ox) + abs(ny - oy)
                v = (d_center, -d_opp, dx, dy)
                if bestv is None or v < bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Pick nearest resource by shortest path heuristic (use 8-neighbor manhattan/diag distance).
    def dist(a, b):
        x1, y1 = a
        x2, y2 = b
        return max(abs(x1 - x2), abs(y1 - y2))  # Chebyshev for 8-way moves

    target = None
    bestt = None
    for r in resources:
        r = tuple(r)
        v = (dist((sx, sy), r), r[0], r[1])
        if bestt is None or v < bestt:
            bestt = v
            target = r

    tx, ty = target

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d_to_t = dist((nx, ny), (tx, ty))
            d_to_opp = dist((nx, ny), (ox, oy))
            # Prefer getting closer to target; tie-break by moving away from opponent; then deterministic.
            v = (d_to_t, -d_to_opp, abs(dx) + abs(dy), dx, dy, nx, ny)
            moves.append((v, [dx, dy]))
    if not moves:
        return [0, 0]

    moves.sort(key=lambda x: x[0])
    return moves[0][1]