def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_target = None
    if resources:
        best_val = None
        for (rx, ry) in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = ds - 0.65 * do + 0.08 * (rx + ry)  # prefer resources that we reach sooner
            if best_val is None or val < best_val or (val == best_val and (rx, ry) < best_target):
                best_val = val
                best_target = (rx, ry)

    def choose_dir(tx, ty):
        candidates = []
        for dx, dy in moves:
            nx = sx + dx
            ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                # tie-break: slightly favor moving "down" (higher y) early to spread over rows
                score = (d, -(ny), -nx)
                candidates.append((score, dx, dy))
        if not candidates:
            return (0, 0)
        candidates.sort(key=lambda t: t[0])
        return (candidates[0][1], candidates[0][2])

    if best_target is not None:
        tx, ty = best_target
        dx, dy = choose_dir(tx, ty)
        return [int(dx), int(dy)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best = None
    for cx, cy in corners:
        if (cx, cy) in obstacles:
            continue
        val = cheb(sx, sy, cx, cy) + 0.02 * cheb(ox, oy, cx, cy) + 0.001 * (cx + cy)
        if best is None or val < best[0] or (val == best[0] and (cx, cy) < best[1]):
            best = (val, cx, cy)
    if best is None:
        return [0, 0]
    dx, dy = choose_dir(best[1], best[2])
    return [int(dx), int(dy)]