def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = obstacles[:]  # list of [x,y]
    can = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Choose best target resource: prefer where we are closer than opponent
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = abs(rx - sx) + abs(ry - sy)
        opd = abs(rx - ox) + abs(ry - oy)
        # primary: advantage (opp - me), secondary: closer to us, tertiary: lower lexicographic
        key = (opd - myd, -myd, -rx * 0.001 - ry * 0.0001, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = [rx, ry]
    tx, ty = best_r

    # Obstacle penalty: avoid stepping onto obstacles and steer away from near obstacles
    def obst_pen(x, y):
        pen = 0
        for px, py in obst:
            if x == px and y == py:
                return 10**9
            dx, dy = x - px, y - py
            v = dx * dx + dy * dy
            if v == 0:
                return 10**9
            # strong near, mild far
            if v <= 4:
                pen += 40
            elif v <= 9:
                pen += 12
            else:
                pen += 3 / v
        return pen

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in can:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_next = abs(nx - tx) + abs(ny - ty)
        # small tie-break: also reduce distance to opponent-target race
        opp_next = abs(nx - ox) + abs(ny - oy)
        # resource race score: smaller my_next is better, larger opp distance to us is better
        score = -my_next * 10 + opp_next * 0.5 - obst_pen(nx, ny)
        # encourage not oscillating: slight preference for moves that progress in target direction
        score += (abs(sx - tx) + abs(sy - ty)) - (abs(nx - tx) + abs(ny - ty))
        # deterministic tie-break by move ordering
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]