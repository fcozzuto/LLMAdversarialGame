def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_row_bias = 1 if oy == sy else 0
    best = None
    best_key = None
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # If opponent is sweeping, contest resources on same row less.
        row_pen = 3 if ty == oy else 0
        # Prefer being first; break ties by absolute advantage, then nearer.
        key = (od - sd - row_pen, sd, -(abs(tx - ox) + abs(ty - oy)), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # One-step lookahead: prefer moves that reduce distance to chosen target.
        nd = cheb(nx, ny, tx, ty)
        cur = cheb(sx, sy, tx, ty)
        val = (cur - nd, -(abs(nx - ox) + abs(ny - oy)), -nd, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]