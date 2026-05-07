def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not res:
        return [0, 0]

    # Choose the resource where we have the largest distance advantage over the opponent.
    best = None
    best_adv = None
    best_ds = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if best is None or adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and (rx, ry) < best))):
            best, best_adv, best_ds = (rx, ry), adv, ds

    if best is None:
        return [0, 0]

    tx, ty = best

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def sign(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    desired_dx = sign(tx - sx)
    desired_dy = sign(ty - sy)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                # allow staying only if we are already best-positioned
                pass
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    # Evaluate candidates by post-move advantage relative to chosen target.
    def move_score(nx, ny, dx, dy):
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        adv2 = do2 - ds2
        # Encourage moving toward target and slightly away from opponent if we can't take advantage.
        towards = -((tx - nx) * desired_dx + (ty - ny) * desired_dy)  # lower is better
        return (adv2, -ds2, -towards, -((dx - desired_dx) * (dx - desired_dx) + (dy - desired_dy) * (dy - desired_dy)))

    best_move = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        key = move_score(nx, ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]