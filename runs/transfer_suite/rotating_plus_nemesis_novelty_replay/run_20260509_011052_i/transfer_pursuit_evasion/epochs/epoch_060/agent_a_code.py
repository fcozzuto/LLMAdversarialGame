def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) or ("agent" in self_role and "evader" not in self_role)
    evader = "evader" in self_role and not pursuer
    resources = observation.get("resources") or []
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax if ax > ay else ay
    target = None
    if resources:
        if evader or not pursuer:
            best = -10**9
            for rx, ry in resources:
                d = dist(sx, sy, rx, ry)
                if d > best:
                    best, target = d, (rx, ry)
        else:
            best = 10**9
            for rx, ry in resources:
                d = dist(sx, sy, rx, ry)
                if d < best:
                    best, target = d, (rx, ry)
    best_score = -10**18
    best_move = (0, 0)
    # deterministic tie-break: higher score first; then prefer (dx,dy) order in dirs
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        opp_d = dist(nx, ny, ox, oy)
        if target is not None:
            res_d = dist(nx, ny, target[0], target[1])
        else:
            res_d = 0
        score = 0
        if target is not None:
            score += (-res_d if (pursuer and not evader) else res_d) * 10
        # interaction with opponent
        score += (opp_d if (evader or not pursuer) else -opp_d) * 5
        if score > best_score:
            best_score, best_move = score, (dx, dy)
    return [best_move[0], best_move[1]]