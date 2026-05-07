def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = set(tuple(p) for p in (observation["obstacles"] or []))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not ok(nx, ny):
            continue
        cur_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            if ds == 0:
                score = 10**12 - man(ox, oy, rx, ry)
            else:
                do = man(ox, oy, rx, ry)
                score = (do - ds) * 100 - ds
            if score > cur_best:
                cur_best = score
        # small preference for positions that are closer to some resource (tie-break stability)
        min_ds = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = man(nx, ny, rx, ry)
            if d < min_ds:
                min_ds = d
        cur_best = cur_best - min_ds * 0.1
        if cur_best > best_score:
            best_score = cur_best
            best_move = [mdx, mdy]

    return [int(best_move[0]), int(best_move[1])]