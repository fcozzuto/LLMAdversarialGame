def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    opp_close = cheb(sx, sy, ox, oy) <= 2
    # If opponent is very close, prioritize moving to safer cells while still preferring progress.
    best_move = (0, 0, -10**18, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): nx, ny = sx, sy

        best_target_adv = -10**18
        best_target_score = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Positive if we are closer than opponent to that resource.
            adv = opd - myd
            # Tie-break: prefer actually making it close.
            score = (adv, -(myd), -((rx + ry) % 2))
            if score > (best_target_adv, best_target_score, 0):  # deterministic update proxy
                best_target_adv = adv
                best_target_score = -(myd)

        dist_me_opp = cheb(nx, ny, ox, oy)
        if opp_close:
            # Safety first, then resource advantage.
            v = (dist_me_opp * 1000) + best_target_adv
            tie = best_target_score
        else:
            # Resource advantage first; keep distance to avoid being trapped.
            v = best_target_adv * 1000 + dist_me_opp
            tie = -cheb(nx, ny, sx, sy)

        # Deterministic tie-breaking: lexicographic by (v, tie, dx, dy)
        cand = (v, tie, dx, dy)
        best = (best_move[2], best_move[3], best_move[0], best_move[1])
        if cand > best:
            best_move = (dx, dy, v, tie)

    return [best_move[0], best_move[1]]