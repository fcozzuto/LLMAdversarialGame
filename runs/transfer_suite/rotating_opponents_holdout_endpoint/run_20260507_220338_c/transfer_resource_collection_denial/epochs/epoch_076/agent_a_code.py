def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            q = (int(p[0]), int(p[1]))
            if 0 <= q[0] < w and 0 <= q[1] < h and q not in obst:
                res.append(q)
    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        ax = int(ax); ay = int(ay); bx = int(bx); by = int(by)
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def target_score(px, py, rx, ry):
        sd = man(px, py, rx, ry)
        od = man(ox, oy, rx, ry)
        return (od - sd, -sd, -rx, -ry)

    # Pick best resource to contest
    best_r = res[0]
    best_sc = None
    for rx, ry in res:
        sc = target_score(sx, sy, rx, ry)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_r = (rx, ry)

    rx, ry = best_r

    # Choose best next step (avoid obstacles) by looking at resulting best target score
    best_move = (0, 0)
    best_move_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obst:
            continue
        # Evaluate move by best resource contest after move
        move_best = None
        for tr, ty in res:
            sc = target_score(nx, ny, tr, ty)
            if move_best is None or sc > move_best:
                move_best = sc
        if best_move_sc is None or move_best > best_move_sc:
            best_move_sc = move_best
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]