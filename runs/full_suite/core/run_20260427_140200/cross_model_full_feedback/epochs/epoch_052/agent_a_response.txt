def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick resource where we have the biggest advantage (opponent farther than us).
    best = None
    best_key = None
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # prefer big gap to opponent; then closer to us
        gap = do - dme
        key = (-gap * 1000, dme)  # gap bigger => key smaller
        # slight tie-break: prefer resources "towards" our side (deterministic)
        side_bias = ((rx <= (w - 1) // 2) ^ (sx <= (w - 1) // 2)) + ((ry <= (h - 1) // 2) ^ (sy <= (h - 1) // 2))
        key = (key[0], key[1] + side_bias)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # If opponent is adjacent to target, switch to next best that reduces their advantage.
    if cheb(ox, oy, tx, ty) <= 1:
        best2 = None
        best2_key = None
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            dme = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (-(do - dme) * 1000, dme)
            if best2_key is None or key < best2_key:
                best2_key = key
                best2 = (rx, ry)
        if best2 is not None:
            tx, ty = best2

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # discourage getting too close to opponent while pursuing target
        key = (d_to_t * 1000, -min(d_opp, 3), abs(dx) + abs(dy))
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]