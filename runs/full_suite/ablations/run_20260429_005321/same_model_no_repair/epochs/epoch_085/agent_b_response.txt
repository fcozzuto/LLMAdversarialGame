def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, cx, cy)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) == (0, 0)):
                best = (d, dx, dy)
        return [best[1], best[2]]

    opp_legal = []
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            opp_legal.append((nx, ny))
    if not opp_legal:
        opp_legal = [(ox, oy)]

    best_move = None
    for dx, dy, nx, ny in legal:
        my_best = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            next_od = min(cheb(px, py, rx, ry) for px, py in opp_legal)
            # Aim to capture resources we are closer to; also avoid giving opponent an easy next grab.
            score = (od - myd) * 100 - myd * 3 - (next_od - myd) * 20
            if my_best is None or score > my_best[0] or (score == my_best[0] and myd < my_best[1]):
                my_best = (score, myd)
        if best_move is None or my_best[0] > best_move[0] or (my_best[0] == best_move[0] and my_best[1] < best_move[1]):
            best_move = (my_best[0], my_best[1], dx, dy)

    return [best_move[2], best_move[3]]