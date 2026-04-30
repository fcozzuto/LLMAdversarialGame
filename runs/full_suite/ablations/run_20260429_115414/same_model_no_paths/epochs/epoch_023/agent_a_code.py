def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    target = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = man(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                target = (rx, ry)

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if target is not None:
            rx, ry = target
            score = -man(nx, ny, rx, ry) - 0.1 * man(nx, ny, ox, oy)
        else:
            score = man(nx, ny, ox, oy) - 0.05 * (abs(nx - (w // 2)) + abs(ny - (h // 2)))
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    if valid(sx + best_move[0], sy + best_move[1]):
        return best_move
    return [0, 0]