def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    best_res = None
    best_key = (-10**9, -10**9)
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd)
        if key > best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]
    tx, ty = best_res

    best_move = (0, 0, -10**9, -10**9)
    for dx, dy, nx, ny in valid_moves:
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        key = (od2 - sd2, -sd2)
        if key > (best_move[2], best_move[3]):
            best_move = (dx, dy, key[0], key[1])

    # If already on target, try to hold; otherwise best step is chosen.
    if (sx, sy) == (tx, ty):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]