def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        resources.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    tx, ty = sx, sy
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # positive means resource closer to self than opponent
            key = (-margin, ds, -rx, -ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp_to_target = cheb(ox, oy, tx, ty)
        d_self_now = cheb(sx, sy, tx, ty)
        improve = d_self_now - d_self
        # prefer moving closer, and when close, prioritize collecting (still deterministic)
        score = (improve, -d_self, -(abs(nx - tx) + abs(ny - ty)), cheb(nx, ny, ox, oy) * 0.01)
        # convert to comparable tuple with deterministic tie-break by dir order
        key = (score[0], score[1], score[2], -score[3], dx, dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]