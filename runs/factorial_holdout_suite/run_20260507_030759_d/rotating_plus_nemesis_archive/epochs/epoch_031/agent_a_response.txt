def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        if man((sx, sy), (ox, oy)) < man((sx, sy), (tx, ty)):
            tx, ty = tx, ty
        best = (10**9, (0, 0))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obst:
                continue
            d = man((nx, ny), (tx, ty))
            if d < best[0]:
                best = (d, (dx, dy))
        return list(best[1])

    best_cell = None
    best_val = (10**9, 10**9)
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
        except Exception:
            continue
        if not inside(rx, ry):
            continue
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        val = (sd - (od // 2), sd)  # prefer resources we reach sooner
        if val < best_val:
            best_val = val
            best_cell = (rx, ry)

    rx, ry = best_cell
    cur_d = man((sx, sy), (rx, ry))
    best_moves = []
    best_step = (10**9, (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        nd = man((nx, ny), (rx, ry))
        # avoid helping opponent by not moving closer unless it improves our distance
        nd_opp = man((nx, ny), (rx, ry)) - (man((ox, oy), (rx, ry)) // 2)
        key = (nd + (0 if nd <= cur_d else 2), nd_opp)
        if key < best_step:
            best_step = key
            best_moves = [(dx, dy)]
        elif key == best_step:
            best_moves.append((dx, dy))

    dx, dy = best_moves[0]
    if dx == 0 and dy == 0:
        # minimal fallback: try any valid move that doesn't increase distance too much
        for dx2, dy2 in dirs:
            nx, ny = sx + dx2, sy + dy2
            if inside(nx, ny) and (nx, ny) not in obst:
                if man((nx, ny), (rx, ry)) <= cur_d:
                    return [dx2, dy2]
        return [0, 0]
    return [dx, dy]