def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Phase shift: first try to pick a resource where we are closer than opponent (material advantage),
    # otherwise deny by aiming at the opponent's closest resource.
    rs = sorted(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]) - cheb(ox, oy, t[0], t[1]), t[0], t[1]))
    my_better = [t for t in rs if cheb(sx, sy, t[0], t[1]) < cheb(ox, oy, t[0], t[1])]
    if my_better:
        target = sorted(my_better, key=lambda t: (cheb(sx, sy, t[0], t[1]), cheb(ox, oy, t[0], t[1]), t[0], t[1]))[0]
    else:
        # Opponent is not worse anywhere we want; pick their closest resource to contest it.
        target = sorted(resources, key=lambda t: (cheb(ox, oy, t[0], t[1]), cheb(sx, sy, t[0], t[1]), t[0], t[1]))[0]

    tx, ty = target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Obstacle handling + deterministic score: prefer moves that reduce our distance to target,
    # while also increasing (or at least not decreasing) opponent distance advantage.
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        # After we move, estimate our progress and how close opponent already is.
        # Also keep us away from dead-ends near obstacles by penalizing adjacency to obstacles.
        adj_obs = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)):
            px, py = nx + ax, ny + ay
            if (px, py) in blocked:
                adj_obs += 1
        # Deny pressure: if opponent could arrive soon, prioritize moves that keep them delayed.
        my_delta = my_d
        deny = cheb(ox, oy, tx, ty) - my_d
        # Higher deny is better, lower my_d is better.
        val = (-my_delta, deny, -adj_obs, nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]