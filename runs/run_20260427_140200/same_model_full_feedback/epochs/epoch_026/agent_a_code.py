def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            d_s = cheb(sx, sy, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            key = (d_s - d_o, d_s, rx, ry)  # primary: we are earlier; secondary: closer; tie: deterministic
            if best_key is None or key < best_key:
                best_key, best_r = key, (rx, ry)
        tx, ty = best_r

        best_move = (0, 0)
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_to = cheb(nx, ny, tx, ty)
            d_from = cheb(sx, sy, tx, ty)
            # Score: prioritize reducing our distance, avoid stepping adjacent to opponent if not improving.
            d_opp_next = cheb(nx, ny, ox, oy)
            d_opp_cur = cheb(sx, sy, ox, oy)
            improve = (d_to - d_from)
            key = (abs(improve), d_to, -d_opp_next, d_opp_next, dx, dy)
            if best_score is None or key < best_score:
                best_score = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward center while keeping away from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_center = cheb(nx, ny, cx, cy)
        d_opp = cheb(nx, ny, ox, oy)
        key = (d_center, -d_opp, dx, dy)  # closer to center, farther from opponent; deterministic tie
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]