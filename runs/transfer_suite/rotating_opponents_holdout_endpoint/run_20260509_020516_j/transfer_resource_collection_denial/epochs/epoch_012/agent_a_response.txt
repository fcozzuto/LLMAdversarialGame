def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    best = None
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    for rx, ry in resources:
        if not inside(rx, ry):
            continue
        myd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - myd
        center = -((rx - cx0) * (rx - cx0) + (ry - cy0) * (ry - cy0))
        key = (adv, -myd, center, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best[1], best[2]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        myd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        adv2 = od2 - myd2
        # If already adjacent, prioritize grabbing by staying/stepping closer to the exact cell.
        grab_bias = -man(nx, ny, tx, ty)
        key = (adv2, -myd2, grab_bias, -abs(nx - ox), -abs(ny - oy), dx, dy)
        if bestm is None or key > bestm[0]:
            bestm = (key, dx, dy)
    return [int(bestm[1]), int(bestm[2])]