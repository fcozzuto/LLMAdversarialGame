def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: prefer resources where we are closer than opponent by the largest margin.
    best = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd  # positive means we are closer
        # Also lightly prefer resources nearer to us to commit.
        key = (-(adv), myd, tx, ty)  # smallest key: we want largest adv -> negative in first? use -adv.
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    # Greedy next step: reduce distance to target, while discouraging moving closer to opponent.
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        my_next = cheb(nx, ny, tx, ty)
        my_now = cheb(sx, sy, tx, ty)
        op_dist = cheb(ox, oy, nx, ny)
        # Prefer improvements; if equal, prefer safer (farther from opponent).
        improve = my_now - my_next
        v = (-improve, my_next, -(op_dist), dx, dy)
        if bestv is None or v < bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]