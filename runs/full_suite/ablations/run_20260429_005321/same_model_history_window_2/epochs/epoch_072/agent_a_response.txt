def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs.sort()

    if not resources:
        # No visible resources: move to reduce distance to opponent (deterministic).
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]] if best else [0, 0]

    best_move = None
    best_val = None

    # Evaluate each move by the best "reach advantage" over opponent among all resources,
    # with a small tiebreaker to keep moving toward a close resource.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_best_adv = -10**9
        my_best_dist = 10**9

        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - md  # positive means I can arrive earlier than opponent
            if adv > my_best_adv or (adv == my_best_adv and md < my_best_dist):
                my_best_adv = adv
                my_best_dist = md

        # Higher is better: prioritize arrival advantage, then closer resource.
        val = (my_best_adv * 1000) - my_best_dist
        cand = (val, dx, dy)

        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move else [0, 0]