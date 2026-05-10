def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obstacle_set = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp(v):
        return -1 if v < -1 else (1 if v > 1 else v)

    if not resources:
        return [0, 0]

    best = None  # (key, tx, ty)
    for rx, ry in resources:
        if (rx, ry) in obstacle_set:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # we are closer if positive
        # prefer slightly more "vertical" progress and closer approach overall
        y_adv = (abs(rx - ox) + abs(ry - oy)) - (abs(rx - sx) + abs(ry - sy))
        key = (lead, y_adv, -ds, -do, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    if best is None:
        return [0, 0]
    _, tx, ty = best

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (None, None)  # (score, (dx,dy))
    for dx, dy in candidates:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacle_set:
            continue
        dcur = cheb(nx, ny, tx, ty)
        # primary: reduce distance to target; secondary: avoid getting closer for opponent
        d_op = cheb(ox, oy, tx, ty)
        score = (-dcur, d_op - cheb(ox, oy, tx, ty), -abs((tx - nx)), -abs((ty - ny)), -dx, -dy)
        if best_move[0] is None or score > best_move[0]:
            best_move = (score, (dx, dy))

    if best_move[1] is None:
        dx = clamp(tx - sx)
        dy = clamp(ty - sy)
        nx = sx + dx
        ny = sy + dy
        if (nx, ny) in obstacle_set or nx < 0 or nx >= w or ny < 0 or ny >= h:
            return [0, 0]
        return [int(dx), int(dy)]

    dx, dy = best_move[1]
    return [int(dx), int(dy)]