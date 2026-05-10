def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid = [(p[0], p[1]) for p in resources if inb(p[0], p[1]) and (p[0], p[1]) not in obstacles]
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # Prefer resources we can reach at least as fast; then maximize advantage; then closer.
        key = (0 if adv >= 0 else 1, -adv, sd, od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Tie-break: prefer immediate progress; if equal, prefer staying safer (closer to nearest resource for next turn).
        if adv >= 0:
            prog_key = (0, nsd, -cheb(nx, ny, tx, ty), -nod)
        else:
            prog_key = (1, 0, nsd, -nod)
        # Additionally, if this move collects the resource, that's best.
        collects = 0 if (nx, ny) == (tx, ty) else 1
        # Deterministic secondary: prefer smaller dx, then dy.
        key = (collects, prog_key[0], prog_key[1], prog_key[2], dx, dy)
        if bestm is None or key < bestm[0]:
            bestm = (key, (dx, dy))
    if bestm is None:
        return [0, 0]
    return [bestm[1][0], bestm[1][1]]