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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource_dist(x, y):
        if not resources:
            return None
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target_x = None
    target_y = None
    if resources:
        pass
    else:
        # move toward corner farthest from opponent
        cx = w - 1 if sx < w // 2 else 0
        cy = h - 1 if sy < h // 2 else 0
        # choose the corner that maximizes distance from opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = -1
        for tx, ty in corners:
            d = cheb(tx, ty, ox, oy)
            if d > best:
                best = d
                target_x, target_y = tx, ty

    def is_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_score = -10**18
    best_move = [0, 0]
    # determinism: fixed tie-breaker order from dirs list
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not is_ok(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)
        if resources:
            d_res = best_resource_dist(nx, ny)
            if d_res is None:
                continue
            # Prefer closer resources, but stay a bit safer from opponent
            score = -d_res + 0.15 * d_op
            # If very close to opponent, reduce risk
            if d_op <= 1:
                score -= 0.5
        else:
            d_goal = cheb(nx, ny, target_x, target_y)
            score = -d_goal + 0.10 * d_op
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move