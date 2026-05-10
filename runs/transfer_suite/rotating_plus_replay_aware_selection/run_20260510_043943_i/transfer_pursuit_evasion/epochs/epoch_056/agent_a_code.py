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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opp_role and "pursuer" not in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_penalty(x, y):
        # prefer being away from obstacles (evader) and not getting trapped (pursuer)
        p = 0
        for (bx, by) in obstacles:
            d = cheb(x, y, bx, by)
            if d == 0: return -10_000
            if d == 1: p += 3
            elif d == 2: p += 1
        return -p

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        # tie-breaker: deterministic based on coordinates
        val = dist if is_evader else -dist
        val += obstacle_penalty(nx, ny) * (1 if is_evader else 0.7)
        key = (val, -nx, -ny) if is_evader else (val, nx, ny)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move