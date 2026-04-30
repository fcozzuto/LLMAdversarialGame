def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (None, -10**18)

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obst:
            continue

        mind = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < mind:
                mind = d

        # Greedy toward nearest resource; slight deterrent vs opponent; gentle center bias.
        my_to_op = cheb(nx, ny, ox, oy)
        center_bias = -abs(nx - cx) - abs(ny - cy)
        score = (-mind * 1000) + (my_to_op * 3) + (center_bias * 2)

        # Deterministic tie-break: prefer moves with smaller (dx,dy) lexicographically.
        if score > best[1]:
            best = ((dx, dy), score)
        elif score == best[1] and best[0] is not None:
            if (dx, dy) < best[0]:
                best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]