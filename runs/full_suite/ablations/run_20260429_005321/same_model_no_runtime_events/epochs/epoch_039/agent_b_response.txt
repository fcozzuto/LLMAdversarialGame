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

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        my = (sx, sy)
        enemy = (ox, oy)
        best = None
        for r in resources:
            d1 = cheb(my, r)
            d2 = cheb(enemy, r)
            # Prefer resources where I'm closer than opponent; then closest for me.
            # Deterministic key: maximize lead, then minimize my distance, then tie-break by position.
            lead = d2 - d1
            key = (lead, -d1, -r[0], -r[1])
            if best is None or key > best[0]:
                best = (key, r)
        target = best[1]
    else:
        target = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None
    cur_t = cheb((sx, sy), target)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_me = cheb((nx, ny), target)
        # Small pressure to deny opponent the same target if possible.
        d_op = cheb((ox, oy), target)
        # Score: prioritize reaching target, then progress beyond current, then keep deterministic tie-break.
        score = (-(d_me), -(d_me - cur_t), -d_op, -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]