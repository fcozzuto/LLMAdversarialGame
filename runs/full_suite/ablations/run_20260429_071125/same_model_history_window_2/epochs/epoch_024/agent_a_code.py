def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    if resources:
        bestd = 10**18
        for x, y in resources:
            d = md(sx, sy, x, y)
            if d < bestd:
                bestd = d
                target = (x, y)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist_op = md(nx, ny, ox, oy)
        edge_pen = abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2)
        if target:
            dist_t = md(nx, ny, target[0], target[1])
            score = -dist_t + 0.8 * dist_op - 0.01 * edge_pen
        else:
            score = 0.8 * dist_op - 0.01 * edge_pen
        if dist_op <= 1:
            score -= 5
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if inside(sx + best_move[0], sy + best_move[1]) else [0, 0]