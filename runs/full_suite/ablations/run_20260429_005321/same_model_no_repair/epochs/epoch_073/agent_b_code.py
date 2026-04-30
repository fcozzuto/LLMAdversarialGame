def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def occ(x, y):
        return (x, y) in obst

    def near_obst_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obst:
                    p += 1
        return p

    # Prefer grabbing a resource earlier than opponent; otherwise reduce relative distance.
    def eval_pos(x, y):
        best_self = 10**9
        best_opp = 10**9
        for rx, ry in resources:
            if occ(rx, ry):
                continue
            ds = cheb(x, y, rx, ry)
            if ds < best_self:
                best_self = ds
            do = cheb(ox, oy, rx, ry)
            if do < best_opp:
                best_opp = do
        # Relative advantage: smaller is better for us.
        rel = best_opp - best_self
        return rel - 0.35 * near_obst_pen(x, y)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if occ(nx, ny):
            continue
        v = eval_pos(nx, ny)

        # Secondary tie-breakers: prefer moving toward nearest resource; then toward center.
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            # Deterministic tie-break using numeric comparison
            cx, cy = w / 2.0, h / 2.0
            cur = cheb(nx, ny, int(cx), int(cy))
            bestx, besty = sx + best_move[0], sy + best_move[1]
            prev = cheb(bestx, besty, int(cx), int(cy))
            if cur < prev:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]