def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def sign(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    best = None
    best_adv = None
    best_ds = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # higher means we are closer than opponent
        if best is None or adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and (rx, ry) < best))):
            best, best_adv, best_ds = (rx, ry), adv, ds

    if best is None:
        return [0, 0]
    tx, ty = best

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_key = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        d1 = cheb(nx, ny, tx, ty)               # progress to our target
        d2 = cheb(nx, ny, ox, oy)              # keep some distance from opponent
        # Key: maximize advantage; then minimize distance to target; then maximize distance from opponent
        our_ds = d1
        opp_do = cheb(ox, oy, tx, ty)
        adv_key = opp_do - our_ds
        key = (adv_key, -d2, -dx, -dy, (nx, ny))
        if best_key is None or key > best_key:
            best_key, best_move = key, [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move