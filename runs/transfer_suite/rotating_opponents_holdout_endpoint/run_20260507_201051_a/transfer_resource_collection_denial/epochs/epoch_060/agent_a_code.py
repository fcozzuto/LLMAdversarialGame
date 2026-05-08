def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def sign(t):
        return 0 if t == 0 else (1 if t > 0 else -1)

    def best_move(tx, ty):
        dirs = [(-1, -1), (0, -1), (1, -1),
                (-1, 0), (0, 0), (1, 0),
                (-1, 1), (0, 1), (1, 1)]
        prefs = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            d_after = cheb(nx, ny, tx, ty)
            primary = d_after
            dx_t, dy_t = sign(tx - sx), sign(ty - sy)
            alignment = - (0 if dx == dx_t else 1) - (0 if dy == dy_t else 1)
            prefs.append((primary, -alignment, nx, ny, dx, dy))
        if not prefs:
            return [0, 0]
        prefs.sort()
        return [prefs[0][4], prefs[0][5]]

    if resources:
        best = None
        best_val = -10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = (do - ds) * 10 - ds  # race resource; tie-break deterministically
            if val > best_val:
                best_val = val
                best = (rx, ry)
            elif val == best_val:
                if (rx, ry) < best:
                    best = (rx, ry)
        tx, ty = best
        return best_move(tx, ty)

    # No resources visible: drift toward opponent's corner to contest lanes
    tx, ty = w - 1, h - 1
    dx, dy = sign(tx - sx), sign(ty - sy)
    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [dx, dy]
    return [0, 0]