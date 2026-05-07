def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def inb(x, y):
        w = observation.get("grid_width", 8)
        h = observation.get("grid_height", 8)
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def sign(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    def best_adv_from(px, py):
        best = None
        best_key = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # higher is better: we get there earlier or closer
            key = (adv, -ds, rx, ry)  # deterministic tie-break
            if best_key is None or key > best_key:
                best = (rx, ry)
                best_key = key
        return best, best_key[0] if best_key else None

    # Evaluate all candidate moves by what they set up (best advantage after move),
    # with a small bias to reduce immediate distance to the currently best target.
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None
    best_tgt = None

    tgt, base_adv = best_adv_from(sx, sy)
    if tgt is None:
        return [0, 0]

    tx, ty = tgt
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ntgt, adv = best_adv_from(nx, ny)
        if ntgt is None:
            continue
        # Prefer moves that keep the same target and reduce distance to it.
        keep = 1 if ntgt == (tx, ty) else 0
        d_to_t = cheb(nx, ny, tx, ty)
        d_now = cheb(sx, sy, tx, ty)
        # Score tuple for deterministic max
        score = (adv, keep, d_now - d_to_t, -abs((nx - ox)) - abs((ny - oy)), -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
            best_tgt = ntgt

    # If somehow none feasible (shouldn't happen), step toward the target.
    if best_score is None:
        return [sign(tx - sx), sign(ty - sy)]
    return best_move