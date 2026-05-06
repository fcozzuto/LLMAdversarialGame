def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = ox, oy
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # Prefer moving away from opponent; tie-break: towards center-ish.
            center = -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)
            cand = (-d, -center, dx, dy)
            if cand < best:
                best = cand
        if best[2] or best[3]:
            return [best[2], best[3]]
        return [0, 0]

    best_score = None
    best_target = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = ds - do
        tie = ds
        cand = (score, tie, rx, ry)
        if best_score is None or cand < best_score:
            best_score = cand
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Primary: reduce our distance to target; Secondary: increase margin vs opponent reach.
        cand = (ns, (ns - no), abs(dx) + abs(dy), dx, dy)
        if cand[:3] < best_move[:3]:
            best_move = cand

    if best_move[3] != 0 or best_move[4] != 0:
        return [int(best_move[3]), int(best_move[4])]
    return [0, 0]