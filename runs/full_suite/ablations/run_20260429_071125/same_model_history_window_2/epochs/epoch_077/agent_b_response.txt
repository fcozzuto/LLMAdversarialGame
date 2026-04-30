def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]
    if any(x == sx and y == sy for (x, y) in resources):
        return [0, 0]

    # Choose a target we can reach sooner than opponent; otherwise pick the nearest good contest.
    best_t = None
    best_v = None
    for x, y in resources:
        d_us = cheb(sx, sy, x, y)
        d_op = cheb(ox, oy, x, y)
        # Strongly prefer resources that are closer for us; slightly prefer those overall closer.
        v = (d_op - d_us) * 1000 - d_us * 10 + (x + y) * 0.001
        if best_v is None or v > best_v:
            best_v = v
            best_t = (x, y)
    tx, ty = best_t

    # Move: avoid obstacles, avoid stepping adjacent to opponent unless it also greatly helps capture.
    best_m = (0, 0)
    best_s = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d_now = cheb(nx, ny, tx, ty)
            d_cur = cheb(sx, sy, tx, ty)
            progress = d_cur - d_now

            d_op_next = cheb(ox, oy, nx, ny)
            adj_pen = 0
            if d_op_next == 1:
                adj_pen = 50
            elif d_op_next == 0:
                adj_pen = 200

            # Ensure we don't "orbit" away from the target: add mild bias toward reducing target distance.
            s = progress * 100 - d_now * 2 - adj_pen
            if best_s is None or s > best_s:
                best_s = s
                best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]