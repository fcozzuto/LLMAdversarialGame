def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if sd <= od:
            key = (0, sd, od, rx, ry)
        else:
            key = (1, od, -sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Prefer the step that reduces Chebyshev distance most; deterministic tie-break.
    cur = cheb(sx, sy, tx, ty)
    cand1 = cheb(sx + dx, sy, tx, ty) if dx != 0 else cur
    cand2 = cheb(sx, sy + dy, tx, ty) if dy != 0 else cur
    if cand1 < cand2:
        return [dx, 0]
    if cand2 < cand1:
        return [0, dy]
    if dx != 0:
        return [dx, 0]
    if dy != 0:
        return [0, dy]
    return [0, 0]