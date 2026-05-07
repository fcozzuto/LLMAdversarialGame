def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Race: choose the move that maximizes (opponent_dist - my_dist) to the best resource,
    # and slightly favors reducing my distance overall.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        score = -10**18
        min_my = 10**9
        for (rx, ry) in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources I'm closer to; among them, closer is better. If I'm not closer,
            # still take the move that makes me "least behind".
            v = (opd - myd) * 100 - myd
            if v > score:
                score = v
            if myd < min_my:
                min_my = myd

        # Small tie-break: keep moving toward resources, and prefer not moving if equal.
        v2 = score * 1_000 - min_my
        if v2 > best_val:
            best_val = v2
            best_move = [dx, dy]
    return best_move