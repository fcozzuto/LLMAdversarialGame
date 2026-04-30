def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man((nx, ny), (cx, cy))
            if d < bestd:
                bestd = d
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_pos = (nx, ny)

        # Pick the resource that gives the best "race" advantage:
        # maximize (opp_distance_to_resource - self_distance_to_resource) with a slight self-distance tie-break.
        best_r_val = -10**18
        for r in resources:
            selfd = man(self_pos, r)
            oppd = man((ox, oy), r)
            v = (oppd - selfd) * 10 - selfd
            if v > best_r_val:
                best_r_val = v

        # Small secondary bias: prefer moves that reduce distance to the best currently-available resource center.
        if best_r_val == -10**18:
            continue
        center_bias = -man(self_pos, ((w - 1) // 2, (h - 1) // 2))
        v_total = best_r_val + center_bias // 3

        if v_total > best_val:
            best_val = v_total
            best_move = [dx, dy]

    return best_move