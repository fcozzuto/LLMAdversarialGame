def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    tx = ty = None
    bestd = 10**9
    if resources:
        for rx, ry in resources:
            d = abs(sx - rx)
            e = abs(sy - ry)
            dd = d if d > e else e
            if dd < bestd:
                bestd = dd
                tx, ty = rx, ry

    if tx is None:
        tx, ty = ox, oy

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_to_target = abs(nx - tx)
        e = abs(ny - ty)
        dist_to_target = dist_to_target if dist_to_target > e else e
        dist_to_opp = abs(nx - ox)
        f = abs(ny - oy)
        dist_to_opp = dist_to_opp if dist_to_opp > f else f
        score = -dist_to_target + (0.05 * dist_to_opp)
        if score > best_score:
            best_score = score
            best_move = [int(dx), int(dy)]
    return best_move