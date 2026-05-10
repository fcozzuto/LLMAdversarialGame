def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if inb(x, y) and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    target = None
    for rx, ry in valid:
        sd = cheb((sx, sy), (rx, ry))
        od = cheb((ox, oy), (rx, ry))
        # Prefer being not slower than opponent, then maximize advantage; deterministic tie.
        key = (od - sd, -sd, -rx, -ry)
        if best is None or key > best:
            best = key
            target = (rx, ry)

    tx, ty = target
    if sx == tx and sy == ty:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic order: iterate in the given order; tie-break by key only.
    cur_sd = cheb((sx, sy), (tx, ty))
    bestm = None
    bestdelta = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            # Engine keeps agent in place; treat it as a stay option with same key as [0,0].
            nx, ny = sx, sy
        nsd = cheb((nx, ny), (tx, ty))
        nod = cheb((ox, oy), (tx, ty))
        # Move that reduces our distance; then keep advantage vs opponent; then prefer advancing toward center.
        center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2)
        key = (-(nsd - cur_sd), (nod - nsd), -nsd, center_bias)
        if bestm is None or key > bestm:
            bestm = key
            bestdelta = [dx, dy]

    return bestdelta