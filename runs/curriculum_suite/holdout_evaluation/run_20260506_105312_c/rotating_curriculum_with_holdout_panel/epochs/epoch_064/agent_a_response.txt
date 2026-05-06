def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources2 = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                resources2.append((rx, ry))
    if not resources2:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (dist(nx, ny, tx, ty), nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_key = None
    best_move = (0, 0)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        # For each resource, prefer moves where we gain over opponent (opp_d - self_d).
        # Also lightly prefer making our distance smaller than opponent (i.e., taking initiative).
        local_best = None
        for rx, ry in resources2:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # advantage score: higher is better => minimize negative
            adv = od - sd
            # encourage reaching first; add slight bias toward nearer resources
            key = (-adv, sd, od, rx, ry)
            if local_best is None or key < local_best:
                local_best = key
        # choose the move that best improves our outcome; deterministic tie-break by move ordering already fixed by iteration
        move_key = local_best if local_best is not None else (0, 0, 0, 0, 0)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]