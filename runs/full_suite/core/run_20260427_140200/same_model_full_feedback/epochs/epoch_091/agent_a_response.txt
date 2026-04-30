def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves.sort(key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]] if best is not None else [0, 0]

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer resources where we become at least as close as opponent (after their next move)
        # Approx: opponent can also move one step, so use (d_op - 1) as their next capability.
        vbest = None
        for rx, ry in resources:
            d_us = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            gap = (d_op - 1) - d_us  # positive => we are closer than they can be
            # Secondary: prefer closer actual arrival for us; tertiary: deterministic tie
            cand = (-(gap * 1000) + d_us, rx, ry)
            if vbest is None or cand < vbest:
                vbest = cand
        # Add mild obstacle/center preference to break ties among equal targets
        center_bias = cheb(nx, ny, w // 2, h // 2)
        total = (vbest[0] + center_bias, vbest[1], vbest[2], dx, dy)
        if best_val is None or total < best_val:
            best_val = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move is not None else [0, 0]