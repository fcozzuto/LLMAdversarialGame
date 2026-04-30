def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    resset = set()
    for r in resources:
        if r and len(r) >= 2:
            resset.add((int(r[0]), int(r[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    # If no resources, head toward opponent corner (deterministic).
    if not resources:
        tx, ty = (0 if ox > w - 1 - ox else w - 1), (0 if oy > h - 1 - oy else h - 1)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                v = -cheb(nx, ny, tx, ty)
                if v > bestv:
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Choose the resource that maximizes our advantage over opponent from this next position.
        best_adv = -10**18
        best_dist = 10**18
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > best_adv or (adv == best_adv and myd < best_dist):
                best_adv = adv
                best_dist = myd

        collect_bonus = 300 if (nx, ny) in resset else 0
        center_bias = -0.01 * cheb(nx, ny, w // 2, h // 2)
        opp_pressure = -0.02 * cheb(nx, ny, ox, oy)  # mild: avoid getting too close if it hurts race outcomes
        score = collect_bonus + 10 * best_adv - best_dist + center_bias + opp_pressure

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]