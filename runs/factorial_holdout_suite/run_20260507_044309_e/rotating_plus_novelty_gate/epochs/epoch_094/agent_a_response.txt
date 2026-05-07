def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    rset = set(tuple(r) for r in resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in rset:
            return [dx, dy]

    if not resources:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best = (10**9, 0, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0] or (d == best[0] and (dx, dy) < (best[2], best[3])):
                best = (d, 0, dx, dy)
        return [best[2], best[3]]

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Maximize how much earlier we reach a resource than opponent.
        local_best = -10**18
        local_d = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            margin = opd - myd
            if margin > local_best or (margin == local_best and myd < local_d):
                local_best = margin
                local_d = myd
        # Tie-break toward moves that keep us closer even when margins tie.
        score = local_best * 1000 - local_d
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]
    return [best_move[0], best_move[1]]