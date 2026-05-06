def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if free(sx + dx, sy + dy):
            return [dx, dy]
        for ddy in [-1, 0, 1]:
            for ddx in [-1, 0, 1]:
                if free(sx + ddx, sy + ddy) and (ddx != 0 or ddy != 0):
                    return [ddx, ddy]
        return [0, 0]

    # Choose a target by maximizing how much closer we are than the opponent.
    best_t = None
    best_adv = -10**9
    for rx, ry in res:
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        adv = opd - myd
        if adv > best_adv:
            best_adv = adv
            best_t = (rx, ry)

    rx, ry = best_t
    # Obstacle-aware single-step: among legal moves, pick one that improves lead to the chosen target;
    # if tied, pick one that reduces our distance to the opponent as a secondary denial tactic.
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            myd2 = dist((nx, ny), (rx, ry))
            opd2 = dist((ox, oy), (rx, ry))
            lead2 = opd2 - myd2
            oppd2 = dist((nx, ny), (ox, oy))
            legal.append((lead2, -myd2, -oppd2, dx, dy))
    if legal:
        legal.sort(reverse=True)
        return [legal[0][3], legal[0][4]]

    return [0, 0]