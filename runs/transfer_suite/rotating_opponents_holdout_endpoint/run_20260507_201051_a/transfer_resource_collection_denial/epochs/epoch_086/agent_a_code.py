def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best = None
    best_sd = 10**9
    best_score = -10**18
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        score = (od - sd) * 1000 - sd
        if score > best_score or (score == best_score and sd < best_sd):
            best_score = score
            best_sd = sd
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    primary = [(dx, 0), (0, dy), (dx, dy), (dx, -dy), (-dx, dy)]
    for step in primary:
        mx, my = step
        if (mx != 0 or my != 0) and valid(sx + mx, sy + my):
            return [mx, my]

    candidates = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]
    for mx, my in candidates:
        if valid(sx + mx, sy + my):
            return [mx, my]
    return [0, 0]