def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    if not resources:
        # No resources: move to maximize distance from opponent (deterministic)
        best = None
        bestv = -10**18
        for nx, ny, dx, dy in candidates:
            v = manh(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target resource that we are relatively closer to than the opponent.
    best_target = resources[0]
    best_tscore = -10**18
    for tx, ty in resources:
        myd = manh(sx, sy, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # Prefer resources we can reach sooner; small tie bias toward larger myd (slightly conservative).
        tscore = (opd - myd) * 10 - myd
        if tscore > best_tscore:
            best_tscore = tscore
            best_target = (tx, ty)

    tx, ty = best_target
    in_resource = (sx, sy) in set(resources)

    # Move one step to improve distance to the target, while keeping away from opponent.
    best = None
    bestv = -10**18
    opp_dist_now = manh(sx, sy, ox, oy)
    for nx, ny, dx, dy in candidates:
        dtn = manh(nx, ny, tx, ty)
        dtop = manh(nx, ny, ox, oy)
        v = -dtn * 100
        if (nx, ny) == (tx, ty):
            v += 2000
        # Avoid walking into easy opponent advantage
        v += (dtop - opp_dist_now) * 2
        # Mild preference to not increase target distance too much
        v += -max(0, dtn - manh(sx, sy, tx, ty)) * 3
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]