def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, ox, oy)
            if best is None or v > best[0] or (v == best[0] and (dx, dy) < (best[1], best[2])):
                best = (v, dx, dy)
        return [best[1], best[2]]

    def obst_near_score(x, y):
        if not blocked: return 0
        dmin = 10**9
        for bx, by in blocked:
            d = cheb(x, y, bx, by)
            if d < dmin: dmin = d
        if dmin <= 1: return -25
        if dmin == 2: return -10
        return 0

    best_val = -10**18
    best_move = (0, 0)
    # Fixed resource iteration order: deterministic even if external ordering varies; keep as is.
    for dx, dy, nx, ny in legal:
        my_best = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Value favors resources we can reach no later than opponent; otherwise penalize.
            win_margin = (op_d - my_d)
            v = win_margin * 120 - my_d * 3
            if my_d == op_d:
                # Tie-break: prefer slightly farther from opponent to avoid contest volatility
                v += (cheb(nx, ny, ox, oy) * -0.5)
            v += obst_near_score(nx, ny)
            if v > my_best:
                my_best = v
        # If multiple moves target equally well, prefer staying closer to opponent early only if non-losing.
        opp_dist = cheb(nx, ny, ox, oy)
        tie = (-opp_dist if my_best > -10**17 else 0)
        cand = (my_best, tie)
        cur_best = (best_val, -cheb(sx + best_move[0], sy + best_move[1], ox, oy))
        if cand[0] > best_val or (cand[0] == best_val and (dx, dy) < best_move):
            best_val = cand[0]
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]