def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("evasion" in r) or ("avoid" in r)

    self_is_evader = is_evader(observation.get("self_role", "")) or is_evader(observation.get("self_role_name", "")) or is_evader(observation.get("role", ""))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    adj = moves

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score(nx, ny):
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # obstacle proximity / cornering penalty
        neigh_free = 0
        for dx, dy in adj:
            tx, ty = nx + dx, ny + dy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                neigh_free += 1
        penalty_box = (8 - neigh_free) * 0.7
        # also discourage stepping adjacent into obstacles too often
        obs_adj = 0
        for dx, dy in adj:
            tx, ty = nx + dx, ny + dy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                obs_adj += 1
        penalty_obs = obs_adj * 0.4
        # resources absent in this task, ignore
        return (-d2 if self_is_evader else d2) - penalty_box - penalty_obs

    best = None
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s = score(nx, ny)
        if best_s is None or s > best_s:
            best_s = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]