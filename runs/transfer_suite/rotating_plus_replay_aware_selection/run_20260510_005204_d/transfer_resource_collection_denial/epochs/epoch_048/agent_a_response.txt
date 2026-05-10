def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick resource with strategic priority: be closer + make opponent farther, but also keep us progressing.
    best_r = None
    best_key = None
    cx0 = (w - 1) / 2.0
    cy0 = (h - 1) / 2.0
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        center = -((rx - cx0) * (rx - cx0) + (ry - cy0) * (ry - cy0))  # closer to center is better
        # Strongly prefer "we are already winning" resources; mild penalty for long races.
        key = (2 * (opd - myd), -myd, center, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate each legal move by: win-margin after move, plus a "progress" term.
    # Also add a small denial term: if opponent is close to target, prefer moves that reduce our distance
    # more than theirs (denier archetype punishes letting them arrive first).
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Progress (lower is better) + margin
        margin = opd2 - myd2
        progress = -myd2
        denial = 0
        # If opponent is currently competitive, prioritize moves that increase our margin sharply.
        if cheb(ox, oy, tx, ty) <= cheb(sx, sy, tx, ty) + 1:
            denial = -max(0, cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty) + 1)
        # Tiny tie-break to avoid dithering: prefer moves that head toward target and not away from center.
        center = -((nx - cx0) * (nx - cx0) + (ny - cy0) * (ny - cy0))
        val = (margin, progress, denial, center, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move