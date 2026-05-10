def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    def obst_adj(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                c += 1
        return c

    # "cut-off" corner target: helps when evader hugs walls
    tx = 0 if ox < w // 2 else w - 1
    ty = 0 if oy < h // 2 else h - 1
    target_corner = (tx, ty)

    best = (0, 0)
    best_score = -10**18 if pursuer else 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        adj = obst_adj(nx, ny)
        d_corner = cheb(nx, ny, target_corner[0], target_corner[1])
        if resources:
            d_res = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        else:
            d_res = 0

        if pursuer:
            score = (-d_op * 120) + (mob * 3) - (d_corner * 2) - (adj * 2) + (0 if not resources else (-d_res * 1))
            if score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            score = (d_op * 120) + (mob * 3) - (d_corner * 2) - (adj * 2) + (0 if not resources else (-d_res * 1))
            if score < best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]