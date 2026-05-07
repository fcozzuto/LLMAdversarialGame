def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx = 3 if sx <= 3 else 4 if sx >= 4 else sx
        ty = 3 if sy <= 3 else 4 if sy >= 4 else sy
        best = None
        for dx, dy, nx, ny in legal:
            v = (cheb(nx, ny, tx, ty), dx, dy)
            if best is None or v < best[0]:
                best = (v, [dx, dy])
        return best[1]

    best = None
    for dx, dy, nx, ny in legal:
        my_best = None
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Race heuristic: prefer moves that reduce my distance and increase opponent distance.
            v = d_my - 0.75 * d_op
            if my_best is None or v < my_best:
                my_best = v
        # Tie-break: prefer closer to some resource when race metric ties, then deterministic dx/dy order.
        close_any = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        v2 = (my_best, close_any, dx, dy)
        if best is None or v2 < best[0]:
            best = (v2, [dx, dy])
    return best[1]