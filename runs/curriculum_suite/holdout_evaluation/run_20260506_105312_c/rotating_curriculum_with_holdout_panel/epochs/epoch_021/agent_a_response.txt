def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a resource where we have a relative edge; if none, pick the closest we can contest.
    best_r = None
    best_rv = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if myd == 0:
            return [0, 0]
        rel = opd - myd  # positive means opponent farther
        # If opponent is closer, prefer resources where we are "not too behind" and can approach defensively.
        if rel < -3:
            continue
        rv = (rel * 14) - myd + (2 if rx in (0, w - 1) or ry in (0, h - 1) else 0) + (1 if (opd >= 2) else 0)
        if rv > best_rv:
            best_rv = rv
            best_r = (rx, ry)

    if best_r is None:
        # Fallback: go to the nearest remaining resource.
        rx, ry = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
        best_r = (rx, ry)

    rx, ry = best_r
    best_m = (0, 0)
    best_mv = -10**18

    # Evaluate candidate next steps with a safety tie-break to avoid obstacle traps.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, rx, ry)
        # Prefer moves that reduce distance to target.
        mv = (-myd * 9)
        # If this move also reduces opponent's "next contest" distance, it's better for denial.
        oppd = cheb(ox, oy, rx, ry)
        mv += (oppd - myd) * 2

        # Safety: count accessible neighbor cells from (nx, ny).
        saf = 0
        for adx, ady in deltas:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) not in obstacles:
                saf += 1
        mv += saf * 0.25

        # Deterministic tie-break: prefer staying only if equally good; otherwise lexicographic on (dx, dy).
        if mv > best_mv or (mv == best_mv and (dx, dy) < best_m):
            best_mv = mv
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]