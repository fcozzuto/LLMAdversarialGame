def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = abs(nx - tx) + abs(ny - ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def dir_step(tx, ty, x, y):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy

    best_res = None
    for rx, ry in resources:
        sd = cheb_dist(sx, sy, rx, ry)
        od = cheb_dist(ox, oy, rx, ry)
        margin = od - sd  # positive means we can reach sooner
        key = (margin, -sd, -(rx + ry))
        if best_res is None or key > best_res[0]:
            best_res = (key, (rx, ry))
    rx, ry = best_res[1]

    tx_step = dir_step(rx, ry, sx, sy)

    close_opp = cheb_dist(sx, sy, ox, oy) <= 2
    best_move = None
    for dx, dy, nx, ny in legal:
        # primary: head toward chosen resource
        to = cheb_dist(nx, ny, rx, ry)
        # secondary: if close to opponent, reduce contact (resource-denier tends to punish proximity)
        opp_d = cheb_dist(nx, ny, ox, oy)
        # tertiary: avoid squares that make opponent also reach us faster next turn
        opp_reach_us = cheb_dist(ox, oy, nx, ny)
        want_dir = 1 if (dx, dy) == tx_step else 0
        score = (want_dir, -to, opp_d if close_opp else 0, -opp_reach_us, -(nx + ny))
        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]