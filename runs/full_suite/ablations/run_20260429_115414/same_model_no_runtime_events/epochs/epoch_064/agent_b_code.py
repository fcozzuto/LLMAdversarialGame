def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a resource where we have the strongest relative advantage (ours closer than opponent).
    target = None
    best = None
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        # Prefer where we are closer; otherwise prefer smallest opponent lead but still reasonable distance.
        key = (-(d2 - d1), d1, rx, ry)  # higher -(d2-d1) means bigger gap in our favor
        if best is None or key > best:
            best = key
            target = (rx, ry)

    # If no resources, head toward opponent's side to contest remaining areas deterministically.
    if target is None:
        tx, ty = 0 if ox > sx else w - 1, 0 if oy > sy else h - 1
    else:
        tx, ty = target

    # One-step greedy move to reduce distance to (tx,ty), but avoid stepping into obstacles.
    currd = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_md = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Tie-break deterministically by preferring moves that also increase our advantage vs opponent.
        adv = 0
        if target is not None:
            adv = (cheb(ox, oy, tx, ty) - nd)
        cand = (-(nd - currd), -adv, dy, dx)
        if best_md is None or cand > best_md:
            best_md = cand
            best_move = (dx, dy)

    # If we didn't improve (blocked/contested), do a deterministic sidestep toward nearest valid cell to target.
    if best_md is not None and best_move == (0, 0):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and cheb(nx, ny, tx, ty) < currd:
                return [dx, dy]
    return [best_move[0], best_move[1]]