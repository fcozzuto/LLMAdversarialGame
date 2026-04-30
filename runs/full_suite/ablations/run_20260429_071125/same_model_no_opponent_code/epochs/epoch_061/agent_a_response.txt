def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = manh((nx, ny), (ox, oy))
            if v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    # Choose nearest resource targets, but prefer stealing (move onto a resource) and pressuring opponent.
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        next_pos = (nx, ny)

        my_pick = 1 if next_pos in res_set else 0
        my_near = 10**9
        opp_near = 10**9
        for r in resources:
            d = manh(next_pos, r)
            if d < my_near:
                my_near = d
            d2 = manh(opp_pos, r)
            if d2 < opp_near:
                opp_near = d2

        # Score: prefer immediate pick, then reduce my distance, and slightly increase relative advantage.
        score = my_pick * 10**6 - my_near * 10 + (opp_near - my_near) * 2
        # Small deterministic tie-break favoring moves that go "up-left" earlier in moves list already.
        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]