def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    res = [(int(p[0]), int(p[1])) for p in (observation.get("resources", []) or [])]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def legal_from(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy):
                out.append((dx, dy, nx, ny))
        return out

    if not res:
        lg = legal_from(sx, sy)
        return [lg[0][0], lg[0][1]] if lg else [0, 0]

    def nearest_dist(px, py):
        best = 10**9
        for tx, ty in res:
            d = cheb(px, py, tx, ty)
            if d < best: best = d
        return best

    def opp_greedy(px, py):
        # choose move that minimizes opponent distance to nearest resource; tie-breaker: maximize distance from us
        best = None; bestd = 10**9; bestt = -10**9
        for ddx, ddy, nx, ny in legal_from(px, py):
            d = nearest_dist(nx, ny)
            tie = cheb(nx, ny, sx, sy)  # keep away from us
            if d < bestd or (d == bestd and tie > bestt):
                bestd = d; bestt = tie; best = (ddx, ddy, nx, ny)
        return best if best is not None else (0, 0, px, py)

    my_legal = legal_from(sx, sy)
    if not my_legal:
        return [0, 0]

    # Identify a couple of target resources deterministically
    targets = sorted(res, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))[:3]

    best_move = None
    best_val = -10**18
    for dx, dy, nx, ny in my_legal:
        # favor moving toward the closest target and "denying" opponent progress by shifting its greedy outcome
        dmin = min(cheb(nx, ny, tx, ty) for tx, ty in targets)
        opp_step = opp_greedy(ox, oy)
        _, _, nox, noy = opp_step
        # predict how much our move changes opponent's ability to approach resources
        opp_dist_after = nearest_dist(nox, noy)
        opp_dist_now = nearest_dist(ox, oy)
        deny = opp_dist_now - opp_dist_after  # positive if opponent gets worse after our move
        # also slightly prefer staying away from opponent to reduce collision chances
        safe = cheb(nx, ny, ox, oy)
        val = (-dmin * 10) + (deny * 6) + (safe * 0.7) + (0.01 * (nx + ny))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]