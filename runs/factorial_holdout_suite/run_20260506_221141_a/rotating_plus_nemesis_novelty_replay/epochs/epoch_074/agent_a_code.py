def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def cd(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    # Prefer resources we can reach earlier than opponent; if not, still take the best available.
    best = None
    best_key = None
    for x, y in resources:
        ds = cd(sx, sy, x, y)
        do = cd(ox, oy, x, y)
        # Tie-break deterministically: lexicographic on (x,y) implicitly via key.
        key = (ds - do * 0.95, ds, do, x, y)
        if best_key is None or key < best_key:
            best_key, best = key, (x, y)
    tx, ty = best

    # Generate candidate moves (deterministic order).
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Choose move that reduces Chebyshev distance to target; then prefers improving advantage.
    best_m = None
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ds1 = cd(nx, ny, tx, ty)
        # Advantage estimate relative to opponent position.
        do1 = cd(ox, oy, tx, ty)
        key = (ds1, (ds1 - do1 * 0.95), dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key, best_m = key, [dx, dy]
    return best_m