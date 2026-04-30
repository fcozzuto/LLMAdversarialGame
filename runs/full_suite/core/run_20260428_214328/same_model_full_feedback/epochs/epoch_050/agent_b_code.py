def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        t = a - c
        if t < 0: t = -t
        u = b - d
        if u < 0: u = -u
        return t + u

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def free_neighbors(x, y):
        cnt = 0
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                cnt += 1
        return cnt

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = man(nx, ny, ox, oy) + 0.2 * free_neighbors(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Greedy race: prefer states that reduce (self_dist - opponent_dist) toward resources,
    # and avoid moves that step into constrained areas.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        fn = free_neighbors(nx, ny)
        # penalty for tightness (avoid traps)
        trap_pen = 3.0 - fn
        trap_pen = trap_pen if trap_pen > 0 else 0.0
        score = 0.0
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Higher is better: being closer than opponent, plus proximity incentive
            score += (do - ds) * 5.0 - ds * 0.3
        score -= trap_pen * 6.0
        if score > bestv:
            bestv = score
            best = (dx, dy)

    return [best[0], best[1]]