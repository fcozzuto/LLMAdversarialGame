def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = (w - 1, h - 1) if cheb(sx, sy, w - 1, h - 1) <= cheb(sx, sy, 0, 0) else (0, 0)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inside(sx + dx, sy + dy):
            return [dx, dy]
        for mx, my in moves:
            if inside(sx + mx, sy + my):
                return [mx, my]
        return [0, 0]

    # Choose target that is relatively closer to us than to opponent (tempo advantage).
    # Also bias away from very contested/near-opponent resources.
    best = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Harder penalty if opponent can arrive no later than us.
        contest = 0
        if do <= ds:
            contest = 2 + (ds - do if ds - do > 0 else 0)
        val = ds - 0.75 * do + contest
        # Tiny tie-breaker for determinism: prefer lower x then y.
        if best is None or val < best_val or (val == best_val and (rx < best[0] or (rx == best[0] and ry < best[1]))):
            best = (rx, ry)
            best_val = val

    tx, ty = best

    # If we are already on a resource, stay/slide minimally: deterministic small move toward opponent to contest next.
    if (sx, sy) == (tx, ty):
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        if inside(sx + dx, sy + dy):
            return [dx, dy]
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if inside(nx, ny):
                return [mx, my]
        return [0, 0]

    # Greedy next-step toward chosen target, with same objective on the next state.
    bestm = (0, 0)
    bestm_val = None
    for mx, my in moves:
        nx, ny = sx + mx, sy