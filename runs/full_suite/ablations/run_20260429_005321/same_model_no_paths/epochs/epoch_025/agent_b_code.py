def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def cell_ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if cell_ok(x, y):
                targets.append((x, y))
        elif isinstance(r, dict):
            x = r.get("x")
            y = r.get("y")
            if x is not None and y is not None and cell_ok(x, y):
                targets.append((int(x), int(y)))
    if not targets:
        targets = [(w // 2, h // 2)]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick best target by current distance advantage.
    best = targets[0]
    best_adv = cheb(ox, oy, best[0], best[1]) - cheb(sx, sy, best[0], best[1])
    for tx, ty in targets[1:]:
        adv = cheb(ox, oy, tx, ty) - cheb(sx, sy, tx, ty)
        if adv > best_adv:
            best_adv = adv
            best = (tx, ty)
    tx, ty = best

    # Evaluate next move: maximize (opponent distance - our distance), break ties by our closer, then fixed order.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        val = (opd - myd, -myd, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]