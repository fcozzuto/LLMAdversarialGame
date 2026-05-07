def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obs_raw = observation.get("obstacles") or []
    obstacles = obs_raw if isinstance(obs_raw, set) else set(tuple(p) for p in obs_raw)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp(v, lo, hi):
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    def best_target():
        best = None
        best_delta = -10**18
        best_ds = 10**18
        best_rx = 10**18
        best_ry = 10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            delta = do - ds
            if (delta > best_delta) or (delta == best_delta and (ds < best_ds or (ds == best_ds and (rx < best_rx or (rx == best_rx and ry < best_ry))))):
                best_delta = delta
                best_ds = ds
                best = (rx, ry)
                best_rx, best_ry = rx, ry
        return best

    def cell_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    rx, ry = best_target()

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_key = (10**9, 10**9, 10**9, 10**9)  # (priority to move, -progress, newx, newy)

    # Prefer taking target if reachable; otherwise reduce distance while keeping safe.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_free(nx, ny):
            continue
        ds_new = cheb(nx, ny, rx, ry)
        do_curr = cheb(ox, oy, rx, ry)
        # priority: immediately reach target; else improve (closer than opponent or faster)
        reach = 0 if ds_new == 0 else 1
        # progress score: how much we beat/close to opponent distance to target
        progress = (do_curr - ds_new)
        key = (reach, -progress, nx, ny)
        if key < best_key:
            best_key = key
            best_move = (dx, dy)

    # If all candidate moves were blocked, fall back deterministically to stay.
    return [int(best_move[0]), int(best_move[1])]