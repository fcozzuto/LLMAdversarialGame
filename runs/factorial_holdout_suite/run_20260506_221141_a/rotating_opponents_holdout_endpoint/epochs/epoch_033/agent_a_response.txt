def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx if dx >= 0 and dx > (dy if dy >= 0 else -dy) else (-dy if dy < 0 else dy) if (dy if dy >= 0 else -dy) > (dx if dx >= 0 else -dx) else (dx if dx >= 0 else -dx)

    # robust chebyshev
    def cheb(ax, ay, bx, by):
        ax -= bx
        ay -= by
        ax = ax if ax >= 0 else -ax
        ay = ay if ay >= 0 else -ay
        return ax if ax > ay else ay

    def advantage(cell):
        rx, ry = cell
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        return (do - ds, -ds)  # higher better

    target = resources[0]
    best = None
    for r in resources:
        sc = advantage(r)
        if best is None or sc > best:
            best = sc
            target = r

    tx, ty = target
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)
    desired = (sx + dx0, sy + dy0)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If desired is valid, still allow tie-breaking by ordering (deterministic).
    scored_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Prefer moves that keep advantage, reduce our distance, and don't drift too far.
        score = (do2 - ds2, -ds2, -abs(nx - tx) - abs(ny - ty), dx, dy)
        scored_moves.append((score, (dx, dy)))

    if not scored_moves:
        return [0, 0]
    scored_moves.sort(reverse=True)
    return [int(scored_moves[0][1][0]), int(scored_moves[0][1][1])]