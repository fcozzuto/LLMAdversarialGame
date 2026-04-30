def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if in_bounds(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if resources:
        best = resources[0]
        bestk = None
        for x, y in resources:
            d_me = cheb(sx, sy, x, y)
            d_op = cheb(ox, oy, x, y)
            tempo = d_op - d_me  # positive if we're closer
            center = -((x - cx) * (x - cx) + (y - cy) * (y - cy))
            k = (tempo, -d_me, center)
            if bestk is None or k > bestk:
                bestk = k
                best = (x, y)
        tx, ty = best
    else:
        # No visible resources: drift to the center-biased point to avoid being corner-trapped.
        tx = int((w - 1) / 2.0 + (0.0 if (observation.get("turn_index", 0) % 2) else 0.5))
        ty = int((h - 1) / 2.0 + (0.0 if (observation.get("turn_index", 0) % 2) else 0.5))
        if not in_bounds(tx, ty):
            tx, ty = sx, sy

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Prefer reducing our distance, keep opponent distance advantage; discourage moving away from center.
        center_pen = ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # Also prefer moves that do not let opponent get closer to that target than us by too much.
        opp_closer = cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty)
        score = (d_op - d_me, -d_me, -center_pen, opp_closer)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]