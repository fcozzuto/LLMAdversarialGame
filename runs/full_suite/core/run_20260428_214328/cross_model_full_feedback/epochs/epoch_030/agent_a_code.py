def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        obst.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = [(int(p[0]), int(p[1])) for p in resources]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Greedy opponent next step toward its nearest resource (approx).
    def opp_next(px, py, target, my_pos):
        tx, ty = target
        best = (px, py)
        bestd = cheb(px, py, tx, ty)
        for ddx, ddy in moves:
            nx, ny = px + ddx, py + ddy
            if inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != my_pos:
                d = cheb(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
                    best = (nx, ny)
        return best

    # If no resources, chase opponent.
    if not res:
        best = None
        bestv = 10**18
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy)
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    # Choose our move by: capture > minimize our distance; while maximizing opponent distance to nearest resource.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        capture = 1 if (nx, ny) in set(res) else 0
        mydist = min(cheb(nx, ny, rx, ry) for rx, ry in res)

        # opponent targets nearest resource to its current position
        t = min(res, key=lambda p: cheb(ox, oy, p[0], p[1]))
        opp_nx, opp_ny = opp_next(ox, oy, t, (nx, ny))
        oppdist = cheb(opp_nx, opp_ny, t[0], t[1])

        # extra: discourage moves that place us adjacent to opponent while not improving our dist much
        adj = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1 and not (nx == ox and ny == oy))

        val = 10000 * capture - 5 * mydist + 3 * oppdist - (15 if adj and mydist > 1 else 0)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]