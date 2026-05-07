def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer: resource where opponent is not closer (maximize od-sd), then smaller sd.
        # Deterministic tie: by coordinates.
        key = (-(od - sd), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    cur_sd = cheb(sx, sy, tx, ty)
    opp_sd = cheb(ox, oy, tx, ty)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                moves.append(((10**9, 10**9, 10**9, 10**9), [0, 0]))
                continue
            nd = cheb(nx, ny, tx, ty)
            # Prefer biggest reduction in our distance; tie-break by keeping opponent farther.
            reduction = cur_sd - nd
            # Opponent doesn't move now, but tie-break by current opp distance to target.
            key = (-reduction, nd, -(opp_sd), dx, dy)
            moves.append((key, [dx, dy]))

    moves.sort(key=lambda t: t[0])
    return moves[0][1]