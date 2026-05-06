def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        best_key = (10**9, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                k = (cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy))
                if k < best_key:
                    best_key = k
                    best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best_move = (0, 0)
    best_key = (10**18, -10**18, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        d_opp = cheb(ox, oy, nx, ny)
        score_key = (d_self, d_opp, -(nx == ox and ny == oy))
        if score_key < best_key:
            best_key = score_key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]