def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs_set = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs_set:
            cands.append((dx, dy, nx, ny))

    if not cands:
        return [0, 0]

    if not resources:
        # Deterministic fallback: move toward opponent if no resources.
        best = (None, -10**18)
        for dx, dy, nx, ny in cands:
            tv = -kdist(nx, ny, ox, oy)
            if tv > best[1]:
                best = ((dx, dy), tv)
        return [best[0][0], best[0][1]]

    # Target resource: maximize (opponent advantage) minus (our distance).
    best_r = None
    best_s = -10**18
    for rx, ry in resources:
        myd = kdist(sx, sy, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        tv = (opd - myd) * 3 - myd * 0.2 + (rx + ry) * 1e-6
        if tv > best_s:
            best_s = tv
            best_r = (rx, ry)

    rx, ry = best_r
    # Choose the move that improves our distance to the chosen resource and blocks opponent approach.
    best = (None, -10**18)
    for dx, dy, nx, ny in cands:
        myd = kdist(nx, ny, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        # Prefer getting closer; if opponent is closer, reduce their advantage by positioning.
        tv = (-myd) * 2 + (opd - myd) * 0.6
        # Tiny deterministic tie-breaker based on coordinates.
        tv += (nx - ny) * 1e-6
        if tv > best[1]:
            best = ((dx, dy), tv)

    return [best[0][0], best[0][1]]