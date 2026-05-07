def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res_set = set(tuple(r) for r in resources)
    valid_steps = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid_steps.append((dx, dy, nx, ny))
    if not valid_steps:
        return [0, 0]

    if (sx, sy) in res_set:
        return [0, 0]

    # Immediate capture
    for dx, dy, nx, ny in valid_steps:
        if (nx, ny) in res_set:
            return [dx, dy]

    # Pick target resource with biggest "reach advantage"
    best = None
    best_key = None
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # prioritize net advantage; tie-break by closer target and deterministic ordering
        key = (do - dme, -(dme), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is not None:
        rx, ry = best
        best_step = None
        best_step_key = None
        for dx, dy, nx, ny in valid_steps:
            # prefer reducing distance to target; slight bonus for staying ahead of opponent
            dme2 = cheb(nx, ny, rx, ry)
            do2 = cheb(ox, oy, rx, ry)
            step_key = (do2 - dme2, -(dme2), -abs(nx - rx) - abs(ny - ry), -dx - dy)
            if best_step_key is None or step_key > best_step_key:
                best_step_key = step_key
                best_step = (dx, dy)
        return [int(best_step[0]), int(best_step[1])]

    # Fallback: head toward the farthest resource direction deterministically
    tx = w - 1 if sx < w // 2 else 0
    ty = h - 1 if sy < h // 2 else 0
    target_x = tx
    target_y = ty
    best_step = None
    bestd = None
    for dx, dy, nx, ny in valid_steps:
        d = cheb(nx, ny, target_x, target_y)
        if bestd is None or d < bestd:
            bestd = d
            best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]