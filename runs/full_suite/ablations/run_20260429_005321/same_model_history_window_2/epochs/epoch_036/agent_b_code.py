def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (0, 0, -10**9)
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sc = -cheb(nx, ny, ox, oy)
            if sc > best[2]:
                best = (nx, ny, sc)
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    # Opponent-aware targeting: maximize lead (my distance smaller than opponent distance)
    best_t = None
    best_key = (-10**18, 10**18, 10**18, 10**18)
    for tx, ty in resources:
        d_me = cheb(sx, sy, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        lead = d_op - d_me
        # Prefer bigger lead, then nearer to target, then deterministic tie-break by coordinates
        key = (lead, -d_me, -abs(tx - 0) - abs(ty - 0), -(tx * 100 + ty))
        if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] > best_key[1]):
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    # Greedy step minimizing our distance to target, but also discourage stepping closer to opponent too much
    best_score = -10**18
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        d2 = cheb(nx, ny, ox, oy)
        # Primary: decrease to target; Secondary: maintain some separation from opponent
        score = (-d1 * 1000) + (d2 * 2)
        if score > best_score:
            best_score = score
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]