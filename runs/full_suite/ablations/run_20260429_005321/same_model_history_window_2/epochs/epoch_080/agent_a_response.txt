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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Deterministic target selection: maximize relative advantage vs opponent, then pick nearest to us
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_key = (-10**18, -10**18)  # (adv, -mydist)
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_me
            key = (adv, -d_me)
            if key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # Evaluate candidate moves: keep away from obstacles, improve our relative advantage on the chosen target,
    # and slightly disrupt opponent by reducing their distance to that target when we can't win it
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_me_now = cheb(nx, ny, tx, ty)
            d_op_now = cheb(ox, oy, tx, ty)
            rel = d_op_now - d_me_now  # larger is better for us
            # tie-break: prefer moves closer to target and farther from obstacles' immediate neighbors
            prox_pen = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    xx, yy = nx + ax, ny + ay
                    if (xx, yy) in obstacles:
                        prox_pen += 1
            score = rel * 100 - d_me_now - prox_pen * 2
            # If opponent is already closer, add a small incentive to get in their way (reduce their progress)
            if d_op_now < d_me_now:
                score += (d_me_now - d_op_now) * -3 + cheb(ox, oy, tx, ty) * 0.01
            cand.append((score, dx, dy))
    cand.sort(key=lambda t: (-(t[0]), t[1], t[2]))
    if not cand:
        return [0, 0]
    return [int(cand[0][1]), int(cand[0][2])]