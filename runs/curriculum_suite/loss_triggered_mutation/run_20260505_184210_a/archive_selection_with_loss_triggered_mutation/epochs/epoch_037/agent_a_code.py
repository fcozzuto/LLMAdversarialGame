def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev: diagonal/straight step costs 1

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cur_best = -10**18
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; also reduce our distance to avoid stalling.
            # Small deterministic tie-breakers: prefer targets closer to center.
            center_bias = -((rx - (w - 1) / 2.0) ** 2 + (ry - (h - 1) / 2.0) ** 2) * 1e-3
            v = (do - ds) * 1000.0 + (-ds) * 1.0 + center_bias
            if v > cur_best:
                cur_best = v
        # Prefer advancing over staying if values equal.
        move_bias = - (abs(dx) + abs(dy)) * 1e-2 if dx == 0 and dy == 0 else 0.0
        vtotal = cur_best + move_bias
        if vtotal > best_val:
            best_val = vtotal
            best = (dx, dy)

    return [int(best[0]), int(best[1])]