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
            if q not in obst:
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

    def pick_best_score(px, py):
        best = None
        best_sc = None
        for rx, ry in res:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # prioritize winning resources first, then shorter self distance
            sc = (od - sd, -sd, -rx, -ry)
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best = (rx, ry, sd, od)
        return best_sc

    # Immediate best move by looking at next-position advantage
    best_move = [0, 0]
    best_move_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            nx, ny = sx, sy  # deterministic: engine would keep in place
        sc = pick_best_score(nx, ny)
        # tie-break: prefer moves that reduce distance to the currently best target
        if best_move_sc is None or sc > best_move_sc:
            best_move_sc = sc
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]