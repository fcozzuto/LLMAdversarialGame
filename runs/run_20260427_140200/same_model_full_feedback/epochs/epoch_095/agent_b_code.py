def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_score = -10**18
    if resources:
        def nearest_dist(x, y):
            md = 10**9
            for rx, ry in resources:
                d = cheb(x, y, rx, ry)
                if d < md:
                    md = d
            return md

        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            rs = nearest_dist(nx, ny)
            os = cheb(nx, ny, ox, oy)
            score = -rs * 10 - os
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            os = cheb(nx, ny, ox, oy)
            score = -os
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    if valid(sx + best_move[0], sy + best_move[1]):
        return best_move
    for dx, dy in dirs:
        if valid(sx + dx, sy + dy):
            return [dx, dy]
    return [0, 0]