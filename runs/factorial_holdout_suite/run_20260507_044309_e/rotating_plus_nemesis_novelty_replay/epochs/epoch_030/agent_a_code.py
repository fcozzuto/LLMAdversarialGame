def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)
    if not res:
        return [0, 0]

    ox, oy = observation.get("opponent_position", (0, 0))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_adv = None
    best_ds = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        if best is None:
            best, best_adv, best_ds = (rx, ry), adv, ds
        else:
            if adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and (rx, ry) < best))):
                best, best_adv, best_ds = (rx, ry), adv, ds

    if best is None:
        return [0, 0]
    tx, ty = best

    def sign(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    desired = (sign(tx - sx), sign(ty - sy))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, tx, ty)
        key = (dist, 0 if (dx, dy) == desired else 1, (nx, ny))
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move