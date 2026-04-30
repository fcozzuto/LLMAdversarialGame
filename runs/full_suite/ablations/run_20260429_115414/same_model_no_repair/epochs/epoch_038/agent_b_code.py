def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2}

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose target with best "arrival advantage" (opponent further than us)
    best_t = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in blocked:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Primary: maximize do-ds (our advantage). Secondary: smaller ds. Tertiary: prefer smaller coords (determinism).
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        # No target: drift to center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        tx, ty = best_t

    best_m = (0, 0)
    best_sc = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy  # engine rejects; simulate staying
            dx, dy = 0, 0
        # Score after move: maximize advantage to target against opponent
        ds_new = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds_new
        # Mild obstacle aversion: penalize if standing adjacent to obstacles (except staying on current cell is fine)
        adj_obs = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            px, py = nx + ax, ny + ay
            if inb(px, py) and (px, py) in blocked:
                adj_obs += 1
        sc = (adv, -ds_new, -adj_obs, -dx, -dy)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]