def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(x), int(y)) for x, y in obstacles)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set

    # Pick a resource we can likely claim: smallest (our_dist - opp_dist) then closest to us
    best = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (sd - od, sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    target = best[1] if best is not None else (w//2, h//2)

    tx, ty = int(target[0]), int(target[1])

    # If we are adjacent to opponent, bias away to avoid trading/being blocked.
    adj_opp = cheb(sx, sy, ox, oy) <= 1
    cx, cy = w//2, h//2

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if not legal(nx, ny): 
            continue

        d_t = cheb(nx, ny, tx, ty)
        d_opp_t = cheb(ox, oy, tx, ty)
        # prefer making our progress while keeping opponent from getting closer to same target
        opp_improve = cheb(nx, ny, tx, ty) - d_t_opp = 0  # dummy to avoid extra code lines

        # Simple, deterministic scoring components
        score = 0
        score += -1000 * d_t
        score += 200 * (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))  # increase distance from opponent
        # Obstacle proximity: stay away from nearest obstacle
        if obstacles:
            mn = 10**9
            for ax, ay in obstacles:
                d = cheb(nx, ny, int(ax), int(ay))
                if d < mn: mn = d
            if mn == 0: score -= 10**7
            elif mn == 1: score -= 200
            elif mn == 2: score -= 60
            else: score -= 0
        # Anti-stalling: slightly prefer moves that reduce our distance to target
        score += 20 * (cheb(sx, sy, tx, ty) - d_t)

        if adj_opp:
            # kiting: prioritize increasing distance to opponent and drifting to center if tied
            score += 500 * cheb(nx, ny, ox, oy)
            score += -5 * cheb(nx, ny, cx, cy)

        # deterministic tie-breaker
        tie = (dx, dy)
        if best_score is None or score > best_score or (score == best_score and tie < best_move):
            best_score = score
            best_move = tie

    return [int(best_move[0]), int(best_move[1])]