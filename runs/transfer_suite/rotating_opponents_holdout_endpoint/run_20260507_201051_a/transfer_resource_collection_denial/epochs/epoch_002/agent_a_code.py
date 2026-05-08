def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    tx, ty = None, None
    best_key = None
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds
            # Prefer resources we can reach first; otherwise the one we deny most (least negative margin).
            key = (margin, -ds, -(rx + ry), rx * 8 + ry)
            if best_key is None or key > best_key:
                best_key = key
                tx, ty = rx, ry
    if tx is None:
        tx, ty = (w // 2, h // 2)

    best = (10**9, -10**9, 0, 0)  # (dist, -margin_next, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dn = cheb(nx, ny, tx, ty)
        ds_next = dn
        do = cheb(ox, oy, tx, ty)
        margin_next = do - ds_next
        cand = (dn, -margin_next, dx, dy)
        if cand < best:
            best = cand

    return [int(best[2]), int(best[3])]