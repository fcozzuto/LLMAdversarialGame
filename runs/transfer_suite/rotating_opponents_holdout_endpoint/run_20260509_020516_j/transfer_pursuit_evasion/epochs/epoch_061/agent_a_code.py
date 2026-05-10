def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in self_role and "evader" in opp_role)

    dirs = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not i_am_evader:
        best = None
        bestv = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d < bestv:
                bestv = d
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # evader: flee while steering toward the farthest corner from pursuer (deterministic)
    best_corner = corners[0]
    bestc = -1
    for c in corners:
        d = cheb(c[0], c[1], ox, oy)
        if d > bestc:
            bestc = d
            best_corner = c

    cx, cy = best_corner
    best = None
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        flee = cheb(nx, ny, ox, oy)
        steer = -cheb(nx, ny, cx, cy)  # closer to corner is better
        val = flee * 1000 + steer  # prioritize fleeing
        if val > bestv:
            bestv = val
            best = [dx, dy]
    return best if best is not None else [0, 0]