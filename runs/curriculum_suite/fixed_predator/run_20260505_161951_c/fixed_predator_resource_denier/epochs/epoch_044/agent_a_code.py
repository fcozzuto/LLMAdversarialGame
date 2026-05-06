def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    resources = observation.get("resources", [])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_move = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            myd_min = 10**9
            oppd_min = 10**9
            best_adv = -10**18
            best_myd_for_adv = 10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                adv = (oppd - myd) * 1000 - myd
                if adv > best_adv or (adv == best_adv and myd < best_myd_for_adv):
                    best_adv = adv
                    best_myd_for_adv = myd
            if best_adv > best_val or (best_adv == best_val and (dx, dy) < best_move):
                best_val = best_adv
                best_move = (dx, dy)
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            dist_op = cheb(nx, ny, ox, oy)
            dist_c = cheb(nx, ny, cx, cy)
            val = dist_op * 100 - dist_c
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]