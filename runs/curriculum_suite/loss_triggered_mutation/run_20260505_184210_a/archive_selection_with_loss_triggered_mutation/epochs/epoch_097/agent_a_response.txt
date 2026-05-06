def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not deltas:
        return [0, 0]

    # Pick a target resource where we have (or will gain) relative closeness vs opponent.
    if res:
        best_t = None
        best_key = None
        for tx, ty in res:
            ds = man(sx, sy, tx, ty)
            do = man(ox, oy, tx, ty)
            adv = do - ds  # positive means we're closer
            key = (-adv, ds, tx, ty)  # prefer high adv (=> low -adv), then closer, then deterministic
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    # Evaluate candidate moves with small heuristic: avoid stepping closer to obstacles and avoid staying still too often.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_opp_to_t = man(ox, oy, tx, ty)
        # If we can reduce our distance relative to opponent, that's good.
        rel = d_opp_to_t - d_to_t
        # Simple obstacle proximity penalty
        neigh_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    neigh_block += 1
        stay_pen = 1 if dx == 0 and dy == 0 else 0
        val = (-rel, d_to_t, stay_pen, neigh_block, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move