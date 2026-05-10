def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacle_set

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_resource_key(px, py):
        # Key: maximize advantage; tie-break by being closer.
        # Using chebyshev because diagonal moves are allowed.
        best = None
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (od - myd, -myd, rx, ry)  # larger advantage, then closer
            if best is None or key > best:
                best = key
        return best

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cur_best = best_resource_key(sx, sy)
    best_move = (0, 0)
    best_key = cur_best

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        k = best_resource_key(nx, ny)
        if k is None:
            continue
        # Prefer moves that improve our key; if equal, prefer staying closer to a likely target.
        if k > best_key:
            best_key = k
            best_move = (dx, dy)
        elif k == best_key:
            if dx == 0 and dy == 0:
                continue
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]