def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = observation.get("resources") or []
    resources = []
    for p in res:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mindist(x, y):
        if not resources:
            return abs(x - w // 2) + abs(y - h // 2)
        best = 10**9
        for rx, ry in resources:
            d = abs(x - rx) + abs(y - ry)
            if d < best:
                best = d
        return best

    def oppdist(x, y):
        return abs(x - ox) + abs(y - oy)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        res_d = mindist(nx, ny)
        o_d = oppdist(nx, ny)
        score = (1000 - 50 * res_d) + (5 * o_d)
        if (nx, ny) in resources:
            score += 500
        if score > best_score:
            best_score = score
            best_move = [int(dx), int(dy)]
    return best_move