def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can secure (ds <= do), then maximize (do-ds).
        # Otherwise take the resource minimizing (ds, do).
        if ds <= do:
            key = (- (do - ds), ds, do, rx, ry)
        else:
            key = (0, ds, do, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    tx, ty = best[1], best[2]

    opp_bias = observation.get("turns_remaining", 0)
    if opp_bias is None:
        opp_bias = 0
    opp_bias = int(opp_bias)

    best_move = (None, None, None)  # (score, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Local greedy: reduce my distance primarily, but also prefer states where I'm relatively ahead.
        ahead = opd - myd
        score = (-ahead, myd, cheb(nx, ny, ox, oy), dx, dy)
        if best_move[0] is None or score < best_move[0]:
            best_move = (score, dx, dy)

    if best_move[1] is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]