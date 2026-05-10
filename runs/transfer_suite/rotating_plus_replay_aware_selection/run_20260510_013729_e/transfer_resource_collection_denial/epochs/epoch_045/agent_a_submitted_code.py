def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set(obstacles)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            moves.append((dx, dy))

    if not moves:
        return [0, 0]
    if not resources:
        return [0, 0]

    best_t = None
    best_key = None
    for rx, ry in resources:
        ad = cheb(sx, sy, rx, ry)
        bd = cheb(ox, oy, rx, ry)
        closer = 0 if ad <= bd else 1
        key = (closer, ad, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    best_m = None
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, tx, ty)
        key = (d, abs(dx) + abs(dy), dx, dy)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]