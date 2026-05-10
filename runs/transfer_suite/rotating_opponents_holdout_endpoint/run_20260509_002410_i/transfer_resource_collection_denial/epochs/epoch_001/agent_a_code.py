def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles if len(p) >= 2}
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    # Pick best target resource deterministically
    best = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gain = do - ds
        key = (gain, -ds, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    if (sx, sy) == (tx, ty):
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            d = cheb(nx, ny, tx, ty)
            # Prefer moves that reduce distance; tie-break deterministically
            moves.append((d, abs(dx) + abs(dy), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    return [int(moves[0][2]), int(moves[0][3])]