def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacle_set

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        max_adv = -10**9
        best_dm = 10**9
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - dm  # positive means we are closer than opponent to that resource after our move
            if adv > max_adv:
                max_adv = adv
                best_dm = dm
            elif adv == max_adv and dm < best_dm:
                best_dm = dm
        # If we can't get ahead on any resource, prioritize reducing our distance to the best resource now.
        if max_adv <= 0:
            now_best = None
            now_best_dm = 10**9
            for rx, ry in resources:
                dm_now = cheb(sx, sy, rx, ry)
                do_now = cheb(ox, oy, rx, ry)
                adv_now = do_now - dm_now
                key = (adv_now, -dm_now)
                if now_best is None or key > now_best:
                    now_best = key
                    now_best_dm = dm_now
            if best_dm > now_best_dm:
                max_adv = -1  # discourage worse-than-now progress
        diag = 1 if dx != 0 and dy != 0 else 0
        # Key: maximize advantage; tie-break by smaller distance; then prefer diagonal; then deterministic move order.
        key = (max_adv, -best_dm, diag, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]