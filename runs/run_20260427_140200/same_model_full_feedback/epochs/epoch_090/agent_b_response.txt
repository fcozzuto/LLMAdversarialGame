def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves.sort(key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    if not resources:
        cx, cy = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            dist = cheb(nx, ny, cx, cy)
            if (dist, -cheb(nx, ny, ox, oy), dx, dy) < best:
                best = (dist, -cheb(nx, ny, ox, oy), dx, dy)
        return [int(best[2]), int(best[3])]

    # Choose a target that we can reach relatively sooner than the opponent.
    best_target = resources[0]
    best_key = (-10**18, 10**18, best_target[0], best_target[1])
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are ahead; tie-break by shorter our distance then lexicographic.
        ahead = do - ds
        key = (ahead, ds, rx, ry)
        if key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Evaluate candidate moves with a new heuristic: move toward target, but also
    # slightly increase distance to opponent if it doesn't hurt progress.
    best_move = (10**18, -10**18, 0, 0)
    cur_d = cheb(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        new_d = cheb(nx, ny, tx, ty)
        step_progress = cur_d - new_d
        opp_sep = cheb(nx, ny, ox, oy)
        # Primary: progress to target, Secondary: separation from opponent, Tertiary: lexicographic move order.
        key = (-step_progress, -opp_sep, dx, dy)
        if key < best_move:
            best_move = key

    return [int(best_move[2]), int(best_move[3])]