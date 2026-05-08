def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((o[0], o[1]) for o in obstacles)

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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        tx = ty = resources[0]
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; break ties by smaller ds.
            key = (ds - do, ds, rx, ry)
            if best is None or key < best:
                best = key
                tx, ty = rx, ry

    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        blocked = 1 if (nx, ny) in obs else 0
        if blocked:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Encourage moves that improve our reach advantage; small distance to target; avoid stepping near obstacles.
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obs:
                    near_obs = 1
                    break
            if near_obs:
                break
        key = (blocked, (d_self - d_opp), d_self, near_obs, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move