def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dx < 0 else -dx

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target = None
    best = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        score = (od - md)  # prefer resources I'm closer to
        if score > best:
            best = score
            target = (rx, ry)
    if target is None:
        # no resources: go toward center, while keeping away from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx, ty = cx, cy
    else:
        tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_sc = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is None:
            my = -(abs(nx - tx) + abs(ny - ty))
        else:
            my = -dist(nx, ny, tx, ty)
        opp = dist(nx, ny, ox, oy)
        sc = my * 10 + opp  # prioritize reaching target, then distance from opponent
        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    # If all moves blocked, stay put (engine will keep in place)
    return [best_mv[0], best_mv[1]]