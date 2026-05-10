def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick our best contestable resource (deterministic tie-break).
    def res_value(cell):
        rx, ry = cell
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Higher adv is better; if tied, smaller myd; then stable coord tie-break
        return (opd - myd, -myd, -rx, -ry)

    target = max(resources, key=res_value)
    tx, ty = target

    # Evaluate candidate moves by improvement toward a contest-winning state.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd_t = cheb(nx, ny, tx, ty)
        opd_t = cheb(ox, oy, tx, ty)
        adv_t = opd_t - myd_t

        # Also softly consider closest resource overall to avoid dead paths.
        best_local = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            v = (opd - myd, -myd, -rx, -ry)
            if best_local is None or v > best_local:
                best_local = v

        # Prefer moves that increase target contestability; then minimize our distance overall; then coordinate.
        score = (adv_t, best_local[1], -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move