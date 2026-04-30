def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_target = resources[0]
        best_d = man(sx, sy, best_target[0], best_target[1])
        for (x, y) in resources[1:]:
            d = man(sx, sy, x, y)
            if d < best_d:
                best_d = d
                best_target = (x, y)
        tx, ty = best_target
    else:
        tx, ty = w // 2, h // 2

    best_move, best_val = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        to_res = man(nx, ny, tx, ty)
        if resources:
            res_score = -to_res
            dist_opp = man(nx, ny, ox, oy)
            opp_score = dist_opp
            val = res_score * 10 + opp_score
        else:
            val = -to_res + man(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    if inside(sx, sy):
        return best_move
    return [0, 0]