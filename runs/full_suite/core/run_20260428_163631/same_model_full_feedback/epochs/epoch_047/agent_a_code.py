def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Exploration bias: alternate target corners deterministically by turn index.
    t = int(observation.get("turn_index") or 0)
    bias_corner = (0, h - 1) if (t % 2 == 0) else (w - 1, 0)

    if not resources:
        # Go toward the biased corner while avoiding obstacles.
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, bias_corner[0], bias_corner[1])
            key = (d, abs(nx - sx) + abs(ny - sy), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return best[1] if best else [0, 0]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Target value: prefer resources we are closer to than the opponent.
        best_for_move = None
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # If we are closer/equal, strongly reward; otherwise penalize.
            rel = d_op - d_me
            # Small attraction to central/bias area to change policy vs last epoch.
            d_bias = cheb(nx, ny, bias_corner[0], bias_corner[1])
            # Compose: maximize rel and minimize distance; turn bias breaks ties deterministically.
            val = (-rel * 2) + d_me + (d_bias * 0.07)
            key = (val, d_me, -rel, abs(rx - nx) + abs(ry - ny), dx, dy)
            if best_for_move is None or key < best_for_move[0]:
                best_for_move = (key, (rx, ry))

        key_move = best_for_move[0]
        if best is None or key_move < best[0]:
            best = (key_move, (dx, dy))

    return list(best[1]) if best else [0, 0]