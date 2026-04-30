def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        best_val = -10**18
        best_ds = 10**9
        best_do = 10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = (do - ds) * 100 - ds  # prefer resources we are closer to, then nearer
            if val > best_val or (val == best_val and ds < best_ds) or (val == best_val and ds == best_ds and do < best_do):
                best_val = val
                best_ds = ds
                best_do = do
                best = (rx, ry)
        tx, ty = best

    def obstacle_penalty(x, y):
        if not inb(x, y): return 10**7
        if (x, y) in obstacles: return 10**6
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) in obstacles:
                    p += 3
        return p

    best_delta = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # also consider making it harder for opponent to reach the same target
        my_adv = (do2 - ds2)
        pen = obstacle_penalty(nx, ny)
        center = -((nx - (w - 1) / 2) ** 2 + (ny - (h - 1) / 2) ** 2) * 0.001
        score = my_adv * 100 - ds2 - pen + center
        # if opponent is already closer, try to move in a way that increases their approach cost
        if not resources:
            score = -ds2 - pen
        if score > best_score:
            best_score = score
            best_delta = [dx, dy]

    return best_delta