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

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = man(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_target = resources[0]
    best_score = -10**18
    resources_sorted = sorted(resources, key=lambda t: (t[0], t[1]))
    for (tx, ty) in resources_sorted:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        score = (do - ds) * 100 - ds  # prefer where we are closer, then nearer
        if score > best_score:
            best_score = score
            best_target = (tx, ty)

    tx, ty = best_target
    best_mv = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_from_o = man(nx, ny, ox, oy)
        v = -d_to_t * 10 + d_from_o  # go to target, keep distance from opponent
        # small tie-break: closer to target first, then lexicographic move for determinism
        if v > best_val or (v == best_val and (d_to_t, dx, dy) < (man(sx + best_mv[0], sy + best_mv[1], tx, ty), best_mv[0], best_mv[1])):
            best_val = v
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]