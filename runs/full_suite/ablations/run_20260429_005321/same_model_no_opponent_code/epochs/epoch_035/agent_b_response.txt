def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    x, y = int(x), int(y)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    res_list = observation.get("resources") or []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if resources and (x, y) in set(resources):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    legal = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # want resources where we're relatively closer
            key = (adv, -ds, -cheb(x, y, rx, ry))
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # If already at target, stay
    if (x, y) == (tx, ty):
        return [0, 0]

    best_move = None
    for dx, dy, nx, ny in legal:
        d = cheb(nx, ny, tx, ty)
        # tie-breakers: prefer moves that also increase our distance advantage over opponent
        adv2 = cheb(ox, oy, tx, ty) - d
        # slight preference to move away from opponent if we're targeting badly
        oppd = cheb(nx, ny, ox, oy)
        key = (-d, adv2, oppd, dx * dx + dy * dy * 0)
        if best_move is None or key > best_move[0]:
            best_move = (key, (dx, dy))

    return [int(best_move[1][0]), int(best_move[1][1])]