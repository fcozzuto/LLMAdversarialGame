def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If no resources visible, retreat toward center to improve future options.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best, bestv = (0, 0), -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -man(sx, sy, tx, ty) + man(nx, ny, tx, ty)  # prefer reducing distance to center
            if v > bestv:
                best, bestv = (dx, dy), v
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18

    # Evaluate each immediate move by the best "advantage" it gives for any visible resource.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer keeping safe distance from opponent unless capturing advantage is strong.
        dist_self_now = man(sx, sy, ox, oy)
        dist_self_new = man(nx, ny, ox, oy)
        safety = dist_self_new - dist_self_now

        # Advantage score: how much closer we are than opponent to the same resource.
        adv_best = -10**18
        for tx, ty in resources:
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            # Strongly prioritize resources where opponent is farther; slight tie-break toward nearer resources.
            adv = (do - ds) * 100 - ds
            # Soft penalty if resource is extremely close to opponent (likely contested).
            adv -= (ds == 0) * 0  # deterministic no-op
            if adv > adv_best:
                adv_best = adv

        # If we can grab immediately, dominate.
        immediate = 1 if (nx, ny) in resources else 0
        v = adv_best + safety + immediate * 1000000
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]