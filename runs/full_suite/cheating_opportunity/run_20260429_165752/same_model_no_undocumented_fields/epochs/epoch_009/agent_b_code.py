def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs.add((int(o[0]), int(o[1])))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))

    if (x, y) in obs:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    if not res:
        target = (w // 2, h // 2)
    else:
        # Pick a resource where we have the biggest distance advantage over the opponent.
        best = None
        best_score = None
        for rx, ry in res:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer winning races; then closer to us.
            score = (od - sd, -sd)
            if best is None or score > best_score:
                best = (rx, ry)
                best_score = score
        target = best

    tx, ty = target
    if (x, y) == (tx, ty):
        return [0, 0]

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Encourage moving to reduce self distance while keeping race advantage.
        val = (od - sd, -sd, -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]