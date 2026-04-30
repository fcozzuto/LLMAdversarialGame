def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    tx, ty = None, None
    if resources:
        bestd = None
        for rx, ry in resources:
            d = abs(rx - sx)
            e = abs(ry - sy)
            dd = d if d > e else e
            if bestd is None or dd < bestd:
                bestd = dd
                tx, ty = rx, ry

    if tx is None:
        tx, ty = w // 2, h // 2

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist_to_target = abs(tx - nx)
        d2 = abs(ty - ny)
        dist_to_target = dist_to_target if dist_to_target > d2 else d2
        dist_to_opp = abs(ox - nx)
        e2 = abs(oy - ny)
        dist_to_opp = dist_to_opp if dist_to_opp > e2 else e2
        score = dist_to_target - 0.1 * dist_to_opp
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move