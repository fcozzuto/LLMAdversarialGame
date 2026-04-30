def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
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
    if not resources:
        return [0, 0]

    res_info = []
    for rx, ry in resources:
        ds = max(abs(sx - rx), abs(sy - ry))
        do = max(abs(ox - rx), abs(oy - ry))
        # prefer resources where we are not too behind
        priority = 0
        if ds <= do:
            priority += 3
        elif ds <= do + 1:
            priority += 1
        else:
            priority -= 1
        # slight preference toward nearer resources
        priority += -0.05 * ds
        res_info.append((priority, rx, ry))

    res_info.sort(reverse=True)
    top = res_info[:6]

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_from(x, y):
        best = -10**9
        for pr, rx, ry in top:
            d = max(abs(x - rx), abs(y - ry))
            # contest-aware: compare to opponent after move
            do = max(abs(ox - rx), abs(oy - ry))
            contest = 3 if d <= do else (1 if d <= do + 1 else -1)
            # if we reach resource, huge
            reach = 50 if d == 0 else 0
            s = contest + pr + reach - 0.3 * d
            if s > best:
                best = s
        # avoid getting too close to opponent (stability)
        opp_d = max(abs(x - ox), abs(y - oy))
        stable = 0.05 * opp_d
        # avoid obstacles
        obst = 0.6 * adj_obst(x, y)
        return best + stable - obst

    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sc = score_from(nx, ny)
            if sc > best_score:
                best_score = sc
                best_move = [dx, dy]
    return best_move