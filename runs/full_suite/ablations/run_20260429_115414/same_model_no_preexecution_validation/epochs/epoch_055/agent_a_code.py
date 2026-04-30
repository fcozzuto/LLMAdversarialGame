def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_gap_from(nx, ny):
        # Maximize how much closer we are than opponent to some resource.
        best = -10**9
        best_r = resources[0]
        for rx, ry in resources:
            gap = cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)
            if gap > best:
                best = gap
                best_r = (rx, ry)
        return best, best_r

    # Decide target by looking at best possible gap from our immediate moves.
    best_overall = -10**9
    chosen = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        gap, (tx, ty) = best_gap_from(nx, ny)

        # Predict opponent next step toward the same target.
        opp_best_d = (0, 0)
        opp_best_dist = 10**9
        for pdx, pdy in dirs:
            px, py = ox + pdx, oy + pdy
            if not legal(px, py):
                continue
            d = cheb(px, py, tx, ty)
            if d < opp_best_dist:
                opp_best_dist = d
                opp_best_d = (pdx, pdy)
        pnx, pny = ox + opp_best_d[0], oy + opp_best_d[1]

        # If we can move onto where opponent is likely to go, prioritize blocking.
        block_bonus = 3.0 if (nx, ny) == (pnx, pny) else 0.0

        # Also prefer moves that reduce our distance to the chosen target.
        my_dist = cheb(nx, ny, tx, ty)
        score = gap + block_bonus - 0.15 * my_dist

        if score > best_overall:
            best_overall = score
            chosen = (dx, dy)

    if legal(sx + chosen[0], sy + chosen[1]):
        return [int(chosen[0]), int(chosen[1])]