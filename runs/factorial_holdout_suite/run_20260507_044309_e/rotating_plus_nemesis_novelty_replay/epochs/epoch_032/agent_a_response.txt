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

    # Pick best resource by relative progress to opponent (deterministic tie-break).
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

    def sign(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    desired_dx = sign(tx - sx)
    desired_dy = sign(ty - sy)

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic preference: closer to desired direction, then maximizes relative advantage, then closer to target.
    best_move = [0, 0]
    best_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        adv = ndo - nds  # bigger is better
        dir_score = -abs(dx - desired_dx) - abs(dy - desired_dy)  # higher is better
        # Key: primary adv, then nds (smaller), then dir_score (higher), then deterministic move order.
        key = (adv, -nds, dir_score, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    # If all candidate moves blocked, stay.
    return best_move if best_key is not None else [0, 0]