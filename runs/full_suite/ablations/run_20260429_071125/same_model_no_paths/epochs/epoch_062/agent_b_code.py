def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (10**9, 0, 0)
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d_op = cheb(nx, ny, ox, oy)
            score = (-d_op, 0, 0)
            key = (-(score[0]), 0, 0)
            if key < best:
                best = key
                best_move = [dx, dy]
        return best_move

    # Choose a target resource: prefer one we can arrive sooner than opponent.
    best_r = None
    best_key = None
    for x, y in resources:
        d_s = cheb(sx, sy, x, y)
        d_o = cheb(ox, oy, x, y)
        # Primary: larger advantage (opp later). Secondary: our distance. Tertiary: stable tie-break.
        adv = d_o - d_s
        key = (-adv, d_s, x * 100 + y)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (x, y)

    tx, ty = best_r
    # Greedy step toward target with safety against opponent (avoid moving closer if tied).
    best_val = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # Prefer smaller distance to target; if equal, prefer larger opponent distance; then stable.
        val = (d_t, -d_o, (nx * 100 + ny))
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move