def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = ox, oy
        best = (10**9, 10**9, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dself = cheb(nx, ny, sx, sy)
            dopp = cheb(nx, ny, tx, ty)
            val = (-dopp, dself)
            if val < (best[0], best[1]):
                best = (val[0], val[1], (dx, dy))
        return best[2] if best[2] is not None else [0, 0]

    best_move = (0, 0)
    best_val = 10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach significantly earlier; slight tie-break to reduce distance to center-ish.
        centerish = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
        val = (ds - 0.9 * do) * 100 + ds + int(centerish)
        if val < best_val:
            best_val = val
            tx, ty = rx, ry

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    desired = (dx, dy)
    nx, ny = sx + desired[0], sy + desired[1]
    if valid(nx, ny):
        return [desired[0], desired[1]]

    # If blocked, choose the move that best reduces Chebyshev distance to target.
    best = (10**9, None)
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        tie = abs(nx - ox) + abs(ny - oy)  # small preference to keep away from opponent
        if (dist, tie) < best[:2]:
            best = (dist, (mdx, mdy))
    return [best[1][0], best[1][1]] if best[1] is not None else [0, 0]