def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        diff = opd - myd
        key = (diff, -myd, -(rx + 31 * ry))
        if best_key is None or key > best_key:
            best_key, best_r = key, (rx, ry)

    rx, ry = best_r
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_mkey = None
    cur_my = cheb(sx, sy, rx, ry)
    cur_opd = cheb(ox, oy, rx, ry)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, rx, ry)
        opd2 = cur_opd  # opponent doesn't move this turn
        # Prefer reducing distance; if tied, prefer more "edge" vs opponent; otherwise reduce worst-case.
        mkey = (-(myd2), -(opd2 - myd2), -(abs((nx - ox)) + abs((ny - oy))), 0)
        if best_mkey is None or mkey > best_mkey or (myd2 < cur_my):
            best_mkey, best_move = mkey, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]