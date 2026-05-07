def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    cx, cy = (gw - 1) // 2, (gh - 1) // 2
    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, cx, cy)
            if (nx, ny) != (sx, sy):
                v += 0.01
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    # Choose a resource that we can beat the opponent to (minimize self distance, maximize win gap).
    best_t = resources[0]
    best_key = (-10**9, -10**9, 10**9)
    for r in resources:
        rx, ry = r[0], r[1]
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        win_gap = od - sd
        # Prefer larger win_gap; then prefer smaller self distance; then deterministic by position.
        key = (win_gap, -sd, rx * 100 + ry)
        if key > best_key:
            best_key = key
            best_t = r

    tx, ty = best_t[0], best_t[1]

    # Decide the next move that most reduces our distance while maintaining "beat" pressure.
    best_move = (0, 0, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        v = (od2 - sd2) * 1000 - sd2
        if (nx, ny) == (sx, sy):
            v -= 1.0
        # Deterministic tie-break: prefer lexicographically smaller (dx,dy) via integer key.
        v += (0.0001 if dx == 0 else 0.0) + (0.00001 if dy == 0 else 0.0)
        if v > best_move[2]:
            best_move = (dx, dy, v)

    return [int(best_move[0]), int(best_move[1])]