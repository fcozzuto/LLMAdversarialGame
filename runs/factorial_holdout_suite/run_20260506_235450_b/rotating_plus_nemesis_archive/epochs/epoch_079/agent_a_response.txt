def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        margin = d_opp - d_me
        key = (margin, -d_me, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((mx, my))

    def score_move(mx, my):
        nx, ny = sx + mx, sy + my
        d_me = cheb(nx, ny, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        return (d_me <= cheb(sx, sy, rx, ry), -d_me, d_opp - d_me, -mx, -my)

    best_m = (0, 0)
    best_m_key = None
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            k = score_move(mx, my)
            if best_m_key is None or k > best_m_key:
                best_m_key = k
                best_m = (mx, my)

    return [int(best_m[0]), int(best_m[1])]