def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    center = (w - 1) / 2.0, (h - 1) / 2.0
    if not resources:
        cx, cy = center
        best = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            key = (cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose move that minimizes (my distance to a resource - advantage vs opponent), with obstacle proximity penalty.
    # Deterministic tie-breakers: dx, dy order.
    def obstacle_proximity_pen(nx, ny):
        pen = 0
        for ax, ay in obstacles:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                pen += 1
        return pen

    best = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_best = None
        score_best = None
        # evaluate nearest "contested" resource by a combined advantage objective
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(nx, ny, ox, oy)  # mild pressure toward opponent? (kept low)
            od_r = cheb(ox, oy, rx, ry)
            advantage = myd - od_r  # lower is better (I closer than opponent)
            # primary: secure close resource; secondary: keep away from opponent; tertiary: avoid obstacles
            val = advantage * 20 + myd * 2 + (od_r == 0) * 10 + obstacle_proximity_pen(nx, ny)
            if score_best is None or val < score_best or (val == score_best and (rx, ry) < my_best):
                score_best = val
                my_best = (rx, ry)
                my_best_obj = (advantage, myd)
        key = (score_best, obstacle_proximity_pen(nx, ny), cheb(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]]