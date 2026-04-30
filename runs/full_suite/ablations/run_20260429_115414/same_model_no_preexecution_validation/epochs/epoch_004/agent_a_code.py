def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, tx, ty)
            key = (d, abs(nx - tx) + abs(ny - ty), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_move = None
    for dx, dy, nx, ny in legal:
        best_key = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            if (rx, ry) in obstacles:
                continue
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            our_adv = our_d - opp_d  # smaller => we are closer than opponent
            key = (our_d, our_adv, abs(nx - rx) + abs(ny - ry))
            if best_key is None or key < best_key:
                best_key = key
        if best_key is None:
            our_d = 10**9
            our_adv = 10**9
            best_key = (our_d, our_adv, 0)
        move_key = (best_key[0], best_key[1], best_key[2], dx, dy, nx, ny)
        if best_move is None or move_key < best_move[0]:
            best_move = (move_key, (dx, dy))

    return [best_move[1][0], best_move[1][1]]