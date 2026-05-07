def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        for mv in ((dx, dy), (dx, 0), (0, dy), (0, 0)):
            nx, ny = sx + mv[0], sy + mv[1]
            if legal(nx, ny):
                return [mv[0], mv[1]]
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; otherwise still pick closest.
        key = (-(sd - od), -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best

    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    moves = ((dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0))
    for mv in moves:
        nx, ny = sx + mv[0], sy + mv[1]
        if not legal(nx, ny):
            continue
        # If stepping onto a resource, take it.
        if (nx, ny) in resources:
            return [mv[0], mv[1]]
    # Final fallback: any legal move that reduces distance to target.
    curd = dist(sx, sy, tx, ty)
    candidates = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1))
    bestm = (0, 0)
    bestv = None
    for mv in candidates:
        nx, ny = sx + mv[0], sy + mv[1]
        if not legal(nx, ny):
            continue
        nd = dist(nx, ny, tx, ty)
        v = (nd < curd, -nd, mv[0], mv[1])
        if bestv is None or v > bestv:
            bestv = v
            bestm = mv
    return [int(bestm[0]), int(bestm[1])]