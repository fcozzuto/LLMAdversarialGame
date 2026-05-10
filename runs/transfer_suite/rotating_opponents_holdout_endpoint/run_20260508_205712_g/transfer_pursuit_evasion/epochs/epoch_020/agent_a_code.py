def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    srole = str(observation.get("self_role", "")).lower()
    self_is_pursuer = ("purs" in srole) or ("chaser" in srole) or ("hunter" in srole) or ("pursuer" in srole)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def obstacle_pen(x, y):
        pen = 0
        if not ok(x, y):
            return 10**6
        # penalize closeness to obstacles to avoid getting boxed in
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                pen += 3
        return pen

    best = None
    best_val = None
    # if possible, head toward/away from opponent directly; else use corner sweep
    if self_is_pursuer:
        target = (ox, oy)
        corner_targets = [(w - 1, h - 1), (0, h - 1), (w - 1, 0), (0, 0)]
    else:
        # maximize distance: prefer farthest corner from opponent
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corner_targets = sorted(corners, key=lambda c: cheb(c[0], c[1], ox, oy), reverse=True)
        target = corner_targets[0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist_to_opp = cheb(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance.
        # incorporate obstacle penalties and slight preference for staying aligned to target.
        align = cheb(nx, ny, target[0], target[1])
        pen = obstacle_pen(nx, ny)
        val = (dist_to_opp if self_is_pursuer else -dist_to_opp) + (0.15 * align) + (0.8 * pen)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        # try any move including staying if all blocked by obstacles
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]