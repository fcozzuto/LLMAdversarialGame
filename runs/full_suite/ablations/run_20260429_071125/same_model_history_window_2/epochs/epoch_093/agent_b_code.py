def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    my_dist0 = cheb(sx, sy, ox, oy)

    if not resources:
        tx = w - 1 if ox <= sx else 0
        ty = h - 1 if oy <= sy else 0
        best = (10**9, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, [dx, dy])
        return best[1] if best[1] is not None else [0, 0]

    # Greedy: pick move that minimizes distance to the closest resource, with penalties for approaching opponent
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if (nx, ny) in res_set:
            return [dx, dy]

        mind = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < mind:
                mind = d

        my_dist = cheb(nx, ny, ox, oy)
        approach = my_dist0 - my_dist  # positive if we moved closer
        edge_bias = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_bias = -0.05  # slight preference for central space to reduce corner traps

        # Higher score is better
        score = (-mind) - 0.35 * approach + edge_bias
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move