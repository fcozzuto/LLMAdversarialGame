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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    preferred = []
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        steal = (do - ds)
        # If opponent closer, strongly prefer to steal; otherwise prefer going to nearest.
        sc = 200 * steal - ds - 2 * abs(tx - sx) - 2 * abs(ty - sy)
        preferred.append((sc, tx, ty))
    preferred.sort(reverse=True)
    target = None
    for sc, tx, ty in preferred:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        if do <= ds + 0:  # opponent is at least as close: attempt steal
            target = (tx, ty)
            break
    if target is None:
        _, tx, ty = preferred[0]
        target = (tx, ty)
    tx, ty = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        # Also consider escaping: don't step into being able to be stolen immediately.
        min_op = 10**9
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            min_op = min(min_op, cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry))
        # Encourage progress to target and reduce opponent advantage.
        score = -ds2 + 5 * min_op
        # If tie, prefer moves that reduce both coords distance (deterministic).
        score -= 0.01 * (abs(nx - tx) + abs(ny - ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]