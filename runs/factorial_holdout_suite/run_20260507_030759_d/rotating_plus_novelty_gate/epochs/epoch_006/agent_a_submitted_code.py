def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        best = [0, 0, 10**9]
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            key = (abs(ddx), abs(ddy), d)
            if key < (best[0], best[1], best[2]):
                best = [abs(ddx), abs(ddy), d]
                bx, by = ddx, ddy
        return [bx if 'bx' in locals() else 0, by if 'by' in locals() else 0]

    rset = set(tuple(r) for r in resources)

    tx, ty = None, None
    bestd = None
    for rx, ry in rset:
        d = abs(sx - rx) + abs(sy - ry)
        key = (d, rx, ry)
        if bestd is None or key < bestd:
            bestd = key
            tx, ty = rx, ry

    best_move = None
    best_key = None
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        key = (d, -((nx, ny) in rset), ddx, ddy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [ddx, ddy]
    return best_move if best_move is not None else [0, 0]