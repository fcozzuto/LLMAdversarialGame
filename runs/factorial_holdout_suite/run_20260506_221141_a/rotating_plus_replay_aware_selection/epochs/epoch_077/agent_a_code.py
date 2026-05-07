def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                v = -cheb(nx, ny, tx, ty)
                if v > bestv:
                    bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best_move, best_val = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        my_best = 10**9
        opp_best = 10**9
        best_s = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources where we are earlier; also prefer closer ones.
            # Tie-break: slight bias to reducing opponent advantage.
            s = 1000 * (d_opp - d_me) - d_me - 0.1 * d_opp
            if s > best_s:
                best_s = s
                my_best = d_me
                opp_best = d_opp

        # Extra shaping: keep moving toward the chosen target by minimizing my_best
        # while not allowing positions that give opponent huge advantage everywhere.
        v = best_s - 0.01 * my_best + 0.005 * (10 - opp_best if opp_best < 10 else 0)
        if v > best_val:
            best_val, best_move = v, (dx, dy)

    return [best_move[0], best_move[1]]