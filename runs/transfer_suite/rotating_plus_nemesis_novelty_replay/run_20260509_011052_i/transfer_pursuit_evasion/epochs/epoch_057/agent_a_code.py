def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    rs = observation.get("scores") or {}
    if isinstance(rs, dict):
        my_score = rs.get("self", rs.get("me", 0))
        opp_score = rs.get("opponent", rs.get("opp", rs.get("enemy", 0)))
    else:
        my_score = 0
        opp_score = 0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    if resources:
        best = None
        for r in resources:
            try:
                rx, ry = r
            except Exception:
                continue
            d = cheb(sx, sy, rx, ry)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        if best is not None:
            target = best[1]

    best_move = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if target is not None:
            val = cheb(nx, ny, target[0], target[1])
        else:
            dist = cheb(nx, ny, ox, oy)
            if my_score <= opp_score:
                val = -dist  # move closer (smaller opponent distance -> larger dist -> more negative)
            else:
                val = dist   # move away
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
        elif best_val == val and best_move is not None and [dx, dy] < best_move:
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]