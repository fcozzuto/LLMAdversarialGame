def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
    obs_list = list(blocked)

    sr = str(observation.get("self_role") or "").lower()
    pursuer = ("pursur" in sr) or ("chaser" in sr) or ("hunter" in sr) or ("tag" in sr) or ("pursuer" in sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_corner_score(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        return max(cheb(x, y, cx, cy) for cx, cy in corners)

    def obstacle_clearance(x, y):
        if not obs_list:
            return 10
        md = 10
        for bx, by in obs_list:
            d = cheb(x, y, bx, by)
            if d < md: md = d
        return md

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue
        d = cheb(nx, ny, ox, oy)
        clr = obstacle_clearance(nx, ny)
        corner = best_corner_score(nx, ny)
        if pursuer:
            key = (d, -clr, -(corner))
        else:
            key = (-d, -clr, -(corner))
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]