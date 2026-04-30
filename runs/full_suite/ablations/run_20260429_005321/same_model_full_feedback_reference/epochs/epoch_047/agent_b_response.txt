def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_t = None
        best_key = None
        for tx, ty in sorted(resources):
            ds = dist2(sx, sy, tx, ty)
            do = dist2(ox, oy, tx, ty)
            key = do - ds  # prefer targets where opponent is farther than us
            if best_key is None or key > best_key or (key == best_key and (tx, ty) < best_t):
                best_key = key
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = (w // 2), (h // 2)

    best_move = (0, 0)
    best_val = None
    cur_ds = dist2(sx, sy, tx, ty)
    cur_do = dist2(ox, oy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = dist2(nx, ny, tx, ty)
        # approximate opponent response by rewarding moves that make the target farther for them too (deterministic proxy)
        # since we can't control opponent position, use a general "tempo": reduce our distance and keep it reducing.
        val = 0
        val += (cur_ds - nds) * 5  # approach our target
        val += (cur_do - dist2(ox, oy, tx, ty)) * 0  # stable term (kept for determinism)
        val += (cur_ds - nds)  # second weight to break ties
        val += -abs(dx) - abs(dy)  # slight preference for not moving diagonally too aggressively
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]