def choose_move(observation):
    w = observation.get("grid_width")
    h = observation.get("grid_height")
    sx, sy = observation.get("self_position")
    ox, oy = observation.get("opponent_position")
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    viable = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            viable.append((dx, dy, nx, ny))
    if not viable:
        return [0, 0]

    if resources:
        tx, ty = resources[0][0], resources[0][1]
        bestd = man(sx, sy, tx, ty)
        for r in resources[1:]:
            rx, ry = r[0], r[1]
            d = man(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                tx, ty = rx, ry
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    oppd = man(ox, oy, tx, ty)
    best = None
    bestv = -10**18
    for dx, dy, nx, ny in viable:
        myd = man(nx, ny, tx, ty)
        sep = man(nx, ny, ox, oy)
        v = (oppd - myd) + 0.03 * sep
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]