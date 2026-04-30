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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # Deterministic obstacle-avoidance: drift away from closer obstacle edge toward center
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, tx, ty)
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Choose target where we can arrive earlier than opponent, with tie-break by earliest and then deterministic order.
    best_target = None
    best_key = None
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        advantage = do - du  # higher is better for us
        # Key: (higher advantage, lower our distance, deterministic position)
        key = (-advantage, du, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    # Select move that reduces our distance to target, while also not suicidally increasing opponent proximity.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_us = cheb(nx, ny, rx, ry)
        d_op = cheb(nx, ny, ox, oy)
        # Slightly penalize moving closer to opponent to contest contested routes.
        score = (d_us, -d_op, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move