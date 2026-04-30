def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx = 0 if sx > w - 1 - sx else w - 1
        ty = 0 if sy > h - 1 - sy else h - 1
        resources = [(tx, ty)]

    # Prefer resources where we are not clearly behind the opponent.
    best_resource = None
    best_metric = 10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        behind = do - ds
        metric = ds + (0 if behind <= 0 else behind * 2)
        if metric < best_metric:
            best_metric = metric
            best_resource = (rx, ry)
    rx, ry = best_resource

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_target = man(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, ox, oy)
        # If opponent is closer to some other resource than us, bias away from leaving that resource.
        leave_pen = 0
        for rx2, ry2 in resources:
            if (rx2, ry2) == (rx, ry):
                continue
            ds2_now = man(sx, sy, rx2, ry2)
            do2 = man(ox, oy, rx2, ry2)
            if do2 - ds2_now >= 2:
                # Keep pressure: don't wander too far from our chosen target if we are behind elsewhere.
                leave_pen += 1 if man(nx, ny, rx, ry) > man(sx, sy, rx, ry) else 0
        score = (-d_target * 3) + (d_opp * 0.6) - (leave_pen * 2)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]