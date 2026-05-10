def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick target resource where we have the strongest distance advantage (ties broken deterministically).
    best = None
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # higher is better
        # Encourage getting to resources that are both reachable soon and not simultaneously favored by opponent.
        key = (-adv, sd, od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), sd, od)

    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # Move that improves progress to target, while maintaining/expanding advantage.
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        adv_after = nod - nsd
        # Secondary: if target is contested, prefer moves that also worsen opponent's reach to target.
        # Tertiary: prefer smaller distance to the next-best resource by light evaluation (no full search).
        secondary = None
        for rx, ry in resources:
            if not legal(rx, ry):
                continue
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # choose the best we can potentially switch to (maximize our advantage; tie deterministic)
            k2 = (-(d2 - d1), d1, d2, rx, ry)
            if secondary is None or k2 < secondary:
                secondary = k2
        # secondary[0] is deterministic; include it in key
        key = (
            -adv_after,
            nsd,
            nod,
            secondary,
            dx, dy,
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move