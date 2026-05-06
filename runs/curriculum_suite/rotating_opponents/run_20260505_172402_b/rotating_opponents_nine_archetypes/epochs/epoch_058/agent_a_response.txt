def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        # drift toward center-ish while avoiding obstacles
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            sdist = abs(nx - tx) + abs(ny - ty)
            cand = (-sdist, 0)  # maximize
            if best is None or cand > best[0]:
                best = (cand, [dx, dy])
        return best[1] if best else [0, 0]

    # choose target resource with best advantage (self faster than opponent)
    best_target = None
    for r in resources:
        sd = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        adv = od - sd  # positive means we are closer/equal in Chebyshev metric
        cand = (adv, -sd, r[0], r[1])
        if best_target is None or cand > best_target[0]:
            best_target = (cand, r)
    target = best_target[1]

    # evaluate moves by resulting advantage toward target, with obstacle avoidance
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        sd_new = cheb((nx, ny), target)
        od_new = cheb((ox, oy), target)
        adv = od_new - sd_new
        # small preference to reduce distance to target; break ties deterministically
        val = (adv, -sd_new, nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_val is not None else [0, 0]