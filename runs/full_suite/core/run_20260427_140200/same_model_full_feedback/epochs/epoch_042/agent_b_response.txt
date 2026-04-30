def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    center = (w // 2, h // 2)

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def nearest_dist(x, y):
        if resources:
            best = 10**9
            for rx, ry in resources:
                d = md(x, y, rx, ry)
                if d < best:
                    best = d
            return best
        return md(x, y, center[0], center[1])

    my_cur = nearest_dist(sx, sy)
    op_cur = nearest_dist(ox, oy)

    best = None
    best_val = -10**18
    # Evaluate moves with a "block" component: prefer moves that worsen opponent prospects.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = nearest_dist(nx, ny)

        # Compute opponent distance after our move by assuming opponent also moves greedily.
        # Deterministic: choose opponent's best single-step move against current resources.
        best_op = 10**9
        for odx, ody in dirs:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            d = nearest_dist(tx, ty)
            if d < best_op:
                best_op = d
        if best_op == 10**9:
            best_op = op_cur

        # Combine: primarily minimize our distance, secondarily maximize opponent distance.
        val = (-my_d * 1000) + (best_op) + (1 if my_d < my_cur else 0)
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best