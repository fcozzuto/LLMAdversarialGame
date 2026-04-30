def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = None

    # If resources exist, we bias toward nearest; otherwise head to center.
    if resources:
        target = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    else:
        target = (w // 2, h // 2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_to_target = cheb(nx, ny, target[0], target[1])

        if resources:
            d_to_resources = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        else:
            d_to_resources = cheb(nx, ny, w // 2, h // 2)

        d_op = cheb(nx, ny, ox, oy)

        # Score: prioritize getting to resources; then keep distance from opponent.
        # Also slightly prefer moving toward target (already via d_to_target).
        val = (0, 0, 0)
        # Convert to single lexicographic comparison: lower is better.
        # Use negative opponent distance to prefer larger d_op.
        key = (d_to_resources, d_to_target, -d_op, dx, dy)

        if best_val is None or key < best_val:
            best_val = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]