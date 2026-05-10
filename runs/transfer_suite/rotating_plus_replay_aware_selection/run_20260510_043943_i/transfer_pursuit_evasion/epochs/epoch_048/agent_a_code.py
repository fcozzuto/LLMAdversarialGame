def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = None
    best_tie = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # tie-breakers: evader to farthest corner, pursuer to nearest corner
        if is_evader:
            corner_d = -min(cheb(nx, ny, cx, cy) for cx, cy in corners)
            score = d  # maximize distance from pursuer
            tie = corner_d
            better = (best is None) or (score > best_score) or (score == best_score and tie > best_tie)
        else:
            corner_d = min(cheb(nx, ny, cx, cy) for cx, cy in corners)
            score = -d  # maximize negative distance = minimize distance
            tie = -corner_d
            better = (best is None) or (score > best_score) or (score == best_score and tie > best_tie)
        if better:
            best = (dx, dy)
            best_score = score
            best_tie = tie

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]