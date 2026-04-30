def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist(a, b):
        # Chebyshev distance for grid+diagonal movement
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    cand_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cand_moves.append((dx, dy, nx, ny))

    if not cand_moves:
        return [0, 0]

    if not resources:
        # With no resources, drift away from opponent toward center-ish deterministically.
        tx, ty = (W - 1) / 2, (H - 1) / 2
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in cand_moves:
            v = dist((nx, ny), (ox, oy)) + 0.01 * (-(abs(nx - tx) + abs(ny - ty)))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Pick a resource that is comparatively closer for us than for the opponent.
    best_r = None
    best_r_key = None
    for r in resources:
        rr = (r[0], r[1])
        ds = dist((sx, sy), rr)
        do = dist((ox, oy), rr)
        # Prefer resources we can reach earlier; break ties deterministically.
        key = (ds - do, ds, rr[0], rr[1])
        if best_r_key is None or key < best_r_key:
            best_r_key = key
            best_r = rr

    tx, ty = best_r
    cur_d_op = dist((sx, sy), (ox, oy))

    # Evaluate one-step move toward target while discouraging becoming closer to opponent.
    best = (0, 0)
    bestv = -10**18
    for dx, dy, nx, ny in cand_moves:
        ndt = dist((nx, ny), (tx, ty))
        ndop = dist((nx, ny), (ox, oy))
        v = -10 * ndt
        if (nx, ny) == (tx, ty):
            v += 250
        # Avoid stepping into likely contested zones (get too close to opponent).
        v += 1.5 * (ndop - cur_d_op)
        # Small deterministic tie-break: prefer staying closer to target x then y.
        v -= 0.001 * (abs(nx - tx) + abs(ny - ty))
        # If opponent can land on target this turn (approx), add extra avoidance.
        if dist((ox, oy), (tx, ty)) <= 1 and ndt <= 1:
            v -= 40
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]