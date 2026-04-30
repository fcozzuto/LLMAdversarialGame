def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) // 2, (h - 1) // 2
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                nx, ny = sx, sy
                dx, dy = 0, 0
            key = (cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            nx, ny = sx, sy
            dx, dy = 0, 0

        best_adv = None
        best_ds = None
        best_center = None
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => we are closer
            key = (-adv, ds, cheb(rx, ry, cx, cy), rx, ry)
            if best_adv is None or key < (-(best_adv), best_ds, best_center, 0, 0):
                best_adv = adv
                best_ds = ds
                best_center = cheb(rx, ry, cx, cy)

        if best_adv is None:
            # Fallback to center
            cand_key = (cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy), 0)
        else:
            # Maximize advantage first, then prefer nearer target and center
            cand_key = (-(best_adv), best_ds, best_center, cheb(nx, ny, ox, oy), dx, dy)

        if best_key is None or cand_key < best_key:
            best_key = cand_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]