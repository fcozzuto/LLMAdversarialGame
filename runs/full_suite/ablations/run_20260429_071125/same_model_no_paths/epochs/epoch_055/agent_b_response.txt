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

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Target: maximize immediate advantage over opponent; if no advantage, pick a safer resource
    best_t = None
    best_s = -10**9
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        s = (do - ds) * 100 - ds  # strongly prefer being closer than opponent
        # small secondary preference: bias toward resources not extremely close to opponent
        s -= (do <= 1) * 25
        if s > best_s:
            best_s = s
            best_t = (rx, ry)

    if best_t is None:
        # fallback: move away from opponent to reduce contest pressure
        best = (0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            dpo = cheb(nx, ny, ox, oy)
            if dpo > best[1]:
                best = (dx, dy), dpo
        (dx, dy), _ = best if isinstance(best[0], tuple) else (best[0], 0)
        return [dx, dy]

    tx, ty = best_t
    # Choose move that minimizes distance to target; tie-break: maximize distance from opponent
    best_move = (0, 0)
    best_val = (10**9, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dt = cheb(nx, ny, tx, ty)
        dpo = cheb(nx, ny, ox, oy)
        val = (dt, -dpo)
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]