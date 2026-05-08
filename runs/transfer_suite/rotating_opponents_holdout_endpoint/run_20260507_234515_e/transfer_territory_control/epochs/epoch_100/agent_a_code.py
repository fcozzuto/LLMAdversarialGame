def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    targets = []
    for k in ("resources", "resource_positions", "remaining_resources"):
        lst = observation.get(k)
        if lst:
            for p in lst:
                if p and len(p) >= 2:
                    t = (int(p[0]), int(p[1]))
                    if inb(t[0], t[1]) and t not in obstacles:
                        targets.append(t)
            if targets:
                break

    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if p and len(p) >= 2:
                t = (int(p[0]), int(p[1]))
                if inb(t[0], t[1]) and t not in obstacles:
                    targets.append(t)
            if len(targets) >= 20:
                break

    if not targets:
        targets = [(w // 2, h // 2)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_score = -10**18
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nt = None
        d_self = 10**9
        d_opp = 10**9
        for t in targets:
            ds = abs(nx - t[0]) + abs(ny - t[1])
            if ds < d_self:
                d_self = ds
                nt = t
        if nt is not None:
            d_opp = abs(ox - nt[0]) + abs(oy - nt[1])
        score = 0
        if nt is not None:
            score += 1000 * (d_opp - d_self)  # prefer targets opponent is worse at
        score += -d_self
        score += 5 * (abs(nx - ox) + abs(ny - oy) < abs(sx - ox) + abs(sy - oy))  # slight avoidance
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move