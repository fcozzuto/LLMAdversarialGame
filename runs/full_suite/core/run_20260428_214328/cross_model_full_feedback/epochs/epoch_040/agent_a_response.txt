def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not res:
        # Head toward opponent slightly (deterministic)
        best = None
        for dx, dy, nx, ny in legal:
            score = cheb(nx, ny, ox, oy)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Choose move that maximizes advantage at a likely target resource:
    # advantage = (my_dist - od_dist) minimized, and also favor reachable resources.
    best_adv = None
    best_move = (0, 0)
    k = 1.25  # reward denying opponent resources
    for dx, dy, nx, ny in legal:
        my_best = None
        for rx, ry in res:
            dme = cheb(nx, ny, rx, ry)
            doe = cheb(ox, oy, rx, ry)
            # lower is better for dme, higher dme relative to doe is worse
            adv = (dme - doe * 0.95) - k * (doe <= dme) + 0.02 * (dme)
            # Prefer resources closer to me while being "better-denial" vs opponent
            if my_best is None or adv < my_best:
                my_best = adv
        # Tie-breaker: prioritize closer to opponent along the same candidate (keeps deterministic)
        opp_pressure = cheb(nx, ny, ox, oy)
        cand = (my_best, opp_pressure)
        if best_adv is None or cand < best_adv:
            best_adv = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]