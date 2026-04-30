def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        best_score = None
        best_ix = None
        for i, (dx, dy) in enumerate(dirs):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            has_res = 1 if (nx, ny) in resources else 0
            score = (has_res, -dist, -cheb(nx, ny, ox, oy))
            if best_score is None or score > best_score or (score == best_score and i < best_ix):
                best_score = score
                best = (dx, dy)
                best_ix = i
        if best is not None:
            return [best[0], best[1]]

    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            best = (dx, dy)
            best_ix = i
            break
    else:
        return [0, 0]

    return [best[0], best[1]]