def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not res:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dco = max(abs(nx - ox), abs(ny - oy))
            v = dco
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best_target = None
    best_metric = -10**18
    for r in res:
        r = tuple(r)
        d_s = cheb((sx, sy), r)
        d_o = cheb((ox, oy), r)
        metric = (d_o - d_s) * 10 - d_s
        if metric > best_metric:
            best_metric = metric
            best_target = r

    tx, ty = best_target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = max(abs(nx - tx), abs(ny - ty))
        d_opp = max(abs(nx - ox), abs(ny - oy))
        score = (-d_self) * 5 + d_opp * 0.5
        if dx == 0 and dy == 0:
            score -= 0.2
        if (nx, ny) == (tx, ty):
            score += 1000
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]