def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # keep moving away from opponent to reduce contention
            d = cheb(nx, ny, ox, oy)
            key = (d, -abs(nx - (w - 1 - ox)) - abs(ny - (h - 1 - oy)))
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return [int(best[1][0]), int(best[1][1])]

    best_move = None
    best_key = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_for_move = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Prefer being closer than opponent; otherwise deny by maximizing gap.
            gap = oppd - myd
            # Small tie-break toward reducing my distance and moving generally toward center.
            center = (w - 1) / 2.0, (h - 1) / 2.0
            cen_dist = abs(nx - center[0]) + abs(ny - center[1])
            key = (gap * 100 - myd * 2 - int(cen_dist), -myd, rx, ry)
            if best_for_move is None or key > best_for_move[0]:
                best_for_move = (key, (rx, ry), myd, oppd)
        move_key = best_for_move[0]
        if best_key is None or move_key > best_key or (move_key == best_key and (dx, dy) < best_move):
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]