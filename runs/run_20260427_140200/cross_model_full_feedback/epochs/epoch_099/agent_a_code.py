def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target = None
    if resources:
        minrx, minry = resources[0]
        bestd = md((mx, my), (minrx, minry))
        for rx, ry in resources[1:]:
            d = md((mx, my), (rx, ry))
            if d < bestd:
                bestd = d
                minrx, minry = rx, ry
        target = (minrx, minry)
    else:
        target = ((w - 1) // 2, (h - 1) // 2)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = mx + dx, my + dy
        if not inb(nx, ny):
            continue
        npos = (nx, ny)

        score = 0
        if resources and npos in set(resources):
            score += 10**6
        score += -md(npos, target)

        d_to_op = md(npos, (ox, oy))
        score += 0.1 * d_to_op

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]