def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_cell = None
    best_key = None
    for (rx, ry) in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer, but also where opponent isn't already winning.
        key = (od - sd, -(sd), -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (rx, ry)

    tx, ty = best_cell
    candidates = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny):
            d = cheb(nx, ny, tx, ty)
            candidates.append((d, mx, my))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [candidates[0][1], candidates[0][2]]