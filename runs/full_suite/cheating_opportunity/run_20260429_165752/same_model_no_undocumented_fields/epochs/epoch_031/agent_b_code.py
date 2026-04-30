def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if resources:
        best = None
        best_key = None
        for x, y in resources:
            sd = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            key = (od - sd, -sd, -x, -y)
            if best_key is None or key > best_key:
                best_key = key
                best = (x, y)
        tx, ty = best
        best_move = (0, 0)
        best_dist = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if best_dist is None or d < best_dist:
                    best_dist = d
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = ox, oy
    best_move = (0, 0)
    best_dist = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny):
            d = cheb(nx, ny, tx, ty)
            if best_dist is None or d < best_dist:
                best_dist = d
                best_move = (dx, dy)
    return [best_move[0], best_move[1]]