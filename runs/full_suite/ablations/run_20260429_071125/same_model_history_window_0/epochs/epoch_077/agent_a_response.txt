def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    self_pos = observation["self_position"]; opp_pos = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    rx = [p[0] for p in resources]; ry = [p[1] for p in resources]
    x, y = self_pos; ox, oy = opp_pos

    def in_bounds(a, b):
        return 0 <= a < w and 0 <= b < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set((p[0], p[1]) for p in resources)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def target_value(nx, ny):
        if not resources:
            cx = w // 2; cy = h // 2
            dmy = cheb(nx, ny, cx, cy); return -dmy
        best = None
        for (px, py) in resources:
            myd = cheb(nx, ny, px, py)
            oppd = cheb(ox, oy, px, py)
            if (px, py) in obstacles:
                continue
            # Prefer resources where we're closer; strongly prefer being closer by a margin.
            margin = oppd - myd
            v = margin * 12 - myd
            if oppd == 1 and myd <= 2:
                v += 25  # disrupt imminent collection
            if myd == 0:
                v += 60  # immediate pickup
            if best is None or v > best:
                best = v
        return best if best is not None else -10**9

    best_move = (0, 0); best_score = -10**18
    for dx, dy in moves:
        nx = x + dx; ny = y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx = x; ny = y
        val = target_value(nx, ny)
        # Tie-break: favor moves that also reduce distance to current best target
        oppd = cheb(ox, oy, nx, ny)
        myd = cheb(nx, ny, x, y)
        score = val - 0.1 * oppd - 0.01 * myd
        if score > best_score:
            best_score = score; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]