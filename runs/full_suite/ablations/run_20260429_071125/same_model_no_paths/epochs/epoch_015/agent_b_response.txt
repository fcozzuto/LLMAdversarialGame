def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not inside(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_t = None
    best_val = -10**18
    for t in resources:
        myd = dist((sx, sy), t)
        opd = dist((ox, oy), t)
        val = (opd - myd) * 100 - myd  # aim for resources where we keep advantage
        if val > best_val:
            best_val = val
            best_t = t

    if best_t is None:
        # No resources: drift to reduce distance to opponent's corner direction (deterministic)
        target = (7 - ox, 7 - oy)
        tx, ty = target
    else:
        tx, ty = best_t

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if best_t is None:
            myd = dist((nx, ny), (tx, ty))
            opd = dist((ox, oy), (tx, ty))
            val = (opd - myd) * 10 - myd
        else:
            myd = dist((nx, ny), (tx, ty))
            opd = dist((ox, oy), (tx, ty))
            # Prefer moves that increase the margin now; tie-break by closer to target
            val = (opd - myd) * 100 - myd
        candidates.append((val, nx, ny, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda z: (-z[0], z[3], z[4]))  # deterministic tie-break
    return [int(candidates[0][3]), int(candidates[0][4])]