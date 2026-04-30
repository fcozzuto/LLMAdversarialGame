def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    center_x, center_y = w // 2, h // 2

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Prefer moving toward center while keeping distance from opponent
            d_op = dist2(nx, ny, ox, oy)
            d_c = dist2(nx, ny, center_x, center_y)
            score = (-d_op, d_c)  # maximize d_op, then minimize d_c
            if best is None or score < best[0]:
                best = (score, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # Choose resource where we have largest relative advantage (closer than opponent)
    def best_resource_for(posx, posy):
        best = None
        for rx, ry in resources:
            ds = dist2(posx, posy, rx, ry)
            do = dist2(ox, oy, rx, ry)
            # Lower is better: our advantage means smaller ds and larger do.
            score = ds - (4.0 * do) / (1 + do)
            tie = (rx, ry)
            key = (score, tie)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1]

    target = best_resource_for(sx, sy)

    # Move one step to improve relative advantage for the chosen target; if equal, improve global advantage
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_t_self = dist2(nx, ny, target[0], target[1])
        d_t_op = dist2(ox, oy, target[0], target[1])
        rel = d_t_self - (4.0 * d_t_op) / (1 + d_t_op)

        # Secondary: how close we are to any resource vs opponent
        sec = 10**18
        for rx, ry in resources:
            ds = dist2(nx, ny, rx, ry)
            do = dist2(ox, oy, rx, ry)
            cur = ds - (4.0 * do) / (1 + do)
            if cur < sec:
                sec = cur

        # Tertiary: keep away from opponent a bit
        keep = -dist2(nx, ny, ox, oy)
        key = (rel, sec, keep, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]