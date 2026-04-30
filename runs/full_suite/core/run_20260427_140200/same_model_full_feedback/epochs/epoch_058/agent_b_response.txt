def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            d = cheb(nx, ny, tx, ty)
            key = (d, -cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    # Precompute distances from opponent to each resource (opponent stays for this heuristic).
    op_to_res = [(cheb(ox, oy, rx, ry), i) for i, (rx, ry) in enumerate(resources)]
    # Deterministically pick top few opponent-closest resources for "blocking" pressure.
    op_to_res.sort()
    k = 4 if len(resources) >= 4 else len(resources)
    hot = [resources[i] for _, i in op_to_res[:k]]

    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue

        my_near = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < my_near: my_near = d

        # "Blocking": reduce our distance to resources that opponent is already near (hot),
        # and increase their effective lead by preferring moves that are not even farther.
        block_score = 0
        for rx, ry in hot:
            d_hot = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Prefer moves that close the gap; large when we are closer or comparable.
            block_score += (op_d - d_hot)

        # Extra: keep some separation from opponent to avoid bad trades.
        sep = cheb(nx, ny, ox, oy)

        # Primary: minimize our nearest distance; Secondary: maximize block gap; Tertiary: maximize separation.
        key = (my_near, -block_score, -sep, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move