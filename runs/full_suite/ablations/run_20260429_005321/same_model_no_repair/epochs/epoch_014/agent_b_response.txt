def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return (w - 1, h - 1)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            ahead = do - ds  # bigger => we are closer
            # Prefer being ahead; then smaller self distance; then deterministic
            key = (-ahead, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        if best is None:
            return (w - 1, h - 1)
        return (best[1], best[2])

    tx, ty = best_target()

    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds_new = cheb(nx, ny, tx, ty)
        ds_cur = cheb(sx, sy, tx, ty)
        # Advantage after move: opponent distance - our distance (we want larger)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds_new
        # Prefer moves that reduce distance; then keep advantage high; then deterministic by position
        move_key = (-(adv), ds_new, (ds_cur - ds_new), nx, ny)
        if best_move is None or move_key < best_move[0]:
            best_move = (move_key, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]