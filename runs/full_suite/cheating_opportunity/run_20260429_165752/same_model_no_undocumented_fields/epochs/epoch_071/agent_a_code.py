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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = [(dx, dy) for dx, dy in moves if free(sx + dx, sy + dy)]
    if not candidates:
        return [0, 0]

    if resources:
        def score_cell(x, y):
            best = 10**9
            for rx, ry in resources:
                d = cheb(x, y, rx, ry)
                if d < best:
                    best = d
            return best
        best_move = None
        best_val = 10**9
        for dx, dy in candidates:
            x, y = sx + dx, sy + dy
            v = score_cell(x, y)
            if v < best_val:
                best_val = v
                best_move = (dx, dy)
        dx, dy = best_move
        return [dx, dy]

    best_move = None
    best_val = 10**9
    for dx, dy in candidates:
        x, y = sx + dx, sy + dy
        v = cheb(x, y, ox, oy)  # with no resources, move toward opponent
        if v < best_val:
            best_val = v
            best_move = (dx, dy)
    dx, dy = best_move
    return [dx, dy]