def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w // 2, h // 2
        bestd, best = 10**9, (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                d = md(nx, ny, tx, ty)
                if d < bestd or (d == bestd and (dx, dy) < best):
                    bestd, best = d, (dx, dy)
        return [best[0], best[1]]

    # Choose a target resource; prefer one we can reach sooner than opponent, otherwise nearest.
    def target_score(rx, ry):
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        return (0 if ds <= do else 1000) + ds - 0.2 * do

    best_r = None
    best_rs = 10**18
    for rx, ry in resources:
        s = target_score(rx, ry)
        if s < best_rs or (s == best_rs and (rx, ry) < best_r):
            best_rs, best_r = s, (rx, ry)

    rx, ry = best_r
    # Move evaluation: head to target; slightly deny opponent's progress to same target; keep away from obstacles.
    def move_eval(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            return 10**18
        ds = md(nx, ny, rx, ry)
        do = md(ox, oy, rx, ry)  # opponent position static this turn
        # Encourage choosing steps that reduce shortest path locally; add small obstacle-adjacency penalty.
        adj_pen = 0
        for tx2 in (nx - 1, nx, nx + 1):
            for ty2 in (ny - 1, ny, ny + 1):
                if (tx2, ty2) in obstacles:
                    adj_pen += 1
        # If we are not currently closest, bias towards moves that increase opponent's lead gap.
        return (ds - 0.35 * do) + 0.02 * adj_pen + (0.001 * (abs(dx) + abs(dy)))

    bestm = (0, 0)
    bestv = 10**18
    for dx, dy in moves:
        v = move_eval(dx, dy)
        if v < bestv or (v == bestv and (dx, dy) < bestm):
            bestv, bestm = v, (dx, dy)
    return [bestm[0], bestm[1]]