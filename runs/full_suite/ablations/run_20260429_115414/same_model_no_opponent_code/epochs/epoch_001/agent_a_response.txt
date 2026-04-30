def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = observation.get('obstacles', []) or []
    obs = {(x, y) for x, y in obstacles}

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (do - ds, -ds, rx, ry)  # prefer resources opponent slower on, then closer, then deterministic
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    moves = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy), (-dx, -dy)]
    best_m = (0, 0)
    best_dist = None
    for mdx, mdy in moves:
        nx = sx + mdx
        ny = sy + mdy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        dist = cheb(nx, ny, tx, ty)
        if best_dist is None or dist < best_dist or (dist == best_dist and (mdx, mdy) < best_m):
            best_dist = dist
            best_m = (mdx, mdy)

    if best_dist is None:
        for mdx in [-1, 0, 1]:
            for mdy in [-1, 0, 1]:
                nx = sx + mdx
                ny = sy + mdy
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obs:
                    continue
                best_m = (mdx, mdy)
                return [mdx, mdy]
        return [0, 0]
    return [best_m[0], best_m[1]]