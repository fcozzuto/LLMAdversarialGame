def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def good_cell(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        return [-dx, -dy]

    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not good_cell(tx, ty):
            continue
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        gain = do - ds  # bigger -> we are relatively closer
        key = (gain, -ds, -tx, -ty)
        if best is None or key > best[0]:
            best = (key, tx, ty)
    _, tx, ty = best

    dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if good_cell(nx, ny):
                dirs.append((dx, dy, nx, ny))
    if not dirs:
        return [0, 0]

    best_move = None
    for dx, dy, nx, ny in dirs:
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        gain = do - ds
        # slight obstacle/edge avoidance via distance to center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        key = (gain, -ds, -center_pen, -abs(tx - nx) - abs(ty - ny), dx, dy)
        if best_move is None or key > best_move[0]:
            best_move = (key, dx, dy)
    return [int(best_move[1]), int(best_move[2])]