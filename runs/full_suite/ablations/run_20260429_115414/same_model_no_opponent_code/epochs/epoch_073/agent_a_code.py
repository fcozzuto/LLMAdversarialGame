def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_sc = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            sc = (od - sd) * 10 - sd
            if best_sc is None or sc > best_sc or (sc == best_sc and (rx, ry) < best):
                best_sc = sc
                best = (rx, ry)
        tx, ty = best

    dx0 = 0
    if tx > sx: dx0 = 1
    elif tx < sx: dx0 = -1
    dy0 = 0
    if ty > sy: dy0 = 1
    elif ty < sy: dy0 = -1

    # Candidate moves: prioritize direct move toward target, then other neighbors that still improve
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        sc = (od - d) * 10 - d
        # tie-break: closer to target in absolute distance, then smallest (dx,dy) deterministically
        candidates.append((sc, -d, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    return [int(candidates[0][2]), int(candidates[0][3])]