def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # If no resources visible, drift toward opponent's side while staying safe.
    if not resources:
        tx, ty = w - 1, h - 1
        best = (-10**18, (0, 0))
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = -cheb(nx, ny, tx, ty)
            if val > best[0]:
                best = (val, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose move that maximizes our advantage to the best contested resource.
    # Advantage = (opp_dist - self_dist), prefer larger advantage; then closer to resource.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_key = (-10**18, -10**18, -10**18, 0, 0)  # (adv, -d, -risk, dx_order, idx)
    best_move = (0, 0)

    for idx, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        best_adv = -10**18
        best_d = 10**18
        # Evaluate best target for this candidate move
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_d):
                best_adv = adv
                best_d = sd
        # Small deterministic "risk": avoid moving closer to obstacles' chebyshev distance if ties
        risk = 0
        if obstacles:
            min_od = 10**18
            for bx, by in obstacles:
                min_od = min(min_od, cheb(nx, ny, bx, by))
            risk = -min_od
        key = (best_adv, -best_d, risk, -abs(dx), idx)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]