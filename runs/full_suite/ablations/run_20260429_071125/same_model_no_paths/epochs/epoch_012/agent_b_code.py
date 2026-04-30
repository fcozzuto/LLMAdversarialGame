def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not inside(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            dO = abs(nx - ox) + abs(ny - oy)
            score = dO
            if score > best[1]:
                best = ([dx, dy], score)
        return best[0] if best[0] is not None else [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Nearest resource distance from candidate next pos
        dR = min(abs(nx - x) + abs(ny - y) for (x, y) in resources)
        # Nearest opponent distance from candidate next pos
        dO = abs(nx - ox) + abs(ny - oy)

        # Prefer approaching resources; prefer staying away from opponent when close.
        # Tie-break deterministically with direction preference toward resources.
        opp_pressure = 0
        if dO <= 2:
            opp_pressure = (3 - dO) * 5  # strong repulsion when very close

        score = (-2.2 * dR) + (0.9 * dO) - opp_pressure

        # Deterministic micro-bias: toward lower-index resource among those tied by dR
        closest = [r for r in resources if (abs(nx - r[0]) + abs(ny - r[1])) == dR]
        if closest:
            tx, ty = min(closest, key=lambda t: (t[0], t[1]))
            dir_bias = -0.01 * (abs(nx - tx) + abs(ny - ty))
            score += dir_bias

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move