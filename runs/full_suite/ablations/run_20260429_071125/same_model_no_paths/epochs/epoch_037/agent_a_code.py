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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    # If no visible resources, drift toward center while keeping away from opponent.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**9
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            v = -cheb(nx, ny, tx, ty) - 0.25 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose action by scoring best resource target for us, with contest penalty.
    # Contest penalty estimates how quickly opponent can reach the same resource.
    best = None
    best_score = -10**18
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # primary: closest resource after move
        best_for_us = 10**9
        scored_target = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < best_for_us:
                best_for_us = d
                scored_target = (rx, ry)

        if scored_target is None:
            score = -cheb(nx, ny, ox, oy)
        else:
            rx, ry = scored_target
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Make it "contest-aware": prefer moves that are both progress and reduce opponent's advantage.
            # Also slightly prefer grabbing closer resources overall.
            score = (-my_d) + 0.9 * (op_d - my_d)
            # small tie-breaker: keep distance from opponent unless we are clearly advantaged
            score += (0.05 if op_d <= my_d else -0.02) * cheb(nx, ny, ox, oy)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]