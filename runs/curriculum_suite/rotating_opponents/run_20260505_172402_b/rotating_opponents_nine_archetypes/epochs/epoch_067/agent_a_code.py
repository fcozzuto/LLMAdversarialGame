def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def score_cell(x, y):
        dxr = x - ox
        dyr = y - oy
        d_op = (dxr * dxr + dyr * dyr) ** 0.5
        if resources:
            best = None
            for rx, ry in resources:
                ddx = x - rx
                ddy = y - ry
                d = (ddx * ddx + ddy * ddy) ** 0.5
                if best is None or d < best:
                    best = d
            return best * 10.0 + d_op
        return d_op

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_move = [0, 0]
    target_x = sx
    target_y = sy
    if resources:
        mx, my = resources[0]
        for rx, ry in resources[1:]:
            if abs(rx - sx) + abs(ry - sy) < abs(mx - sx) + abs(my - sy):
                mx, my = rx, ry
        target_x, target_y = mx, my
    else:
        target_x, target_y = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        s = score_cell(nx, ny)
        tie = abs(nx - target_x) + abs(ny - target_y)
        if best is None or s < best or (s == best and tie < (abs(best_move[0] + sx - target_x) + abs(best_move[1] + sy - target_y))):
            best = s
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]