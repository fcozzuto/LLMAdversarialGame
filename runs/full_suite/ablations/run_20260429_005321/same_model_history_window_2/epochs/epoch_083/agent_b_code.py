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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = w // 2, h // 2

    target = None
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer being closer; then make it harder for opponent; then deterministic tie-break.
            key = (d_me, -d_op, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        target = best
    else:
        target = (cx, cy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_me = cheb(nx, ny, target[0], target[1])
        d_op = cheb(ox, oy, target[0], target[1])
        # Secondary: keep moving toward the chosen target and away from being "stuck" (prefer lower dist-to-center too).
        key = (d_me, -d_op, cheb(nx, ny, cx, cy), dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    # If all candidate moves were blocked, fall back to staying still (engine will keep position).
    return [int(best_move[0]), int(best_move[1])]