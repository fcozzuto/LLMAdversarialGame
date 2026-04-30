def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-999999, 999999, 999999)  # score, then -resource_dist, then opponent_dist
    best_move = (0, 0)

    target_list = resources if resources else [(ox, oy)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if resources:
            rd = min(manh((nx, ny), r) for r in resources)
        else:
            rd = man((nx, ny), (ox, oy))
        od = man((nx, ny), (ox, oy))
        score = -rd + (1 if (dx == 0 and dy == 0) else 0) - (0 if resources else 0)
        # Deterministic tie-break: higher score, then smaller rd, then smaller od, then smaller dx,dy lexicographically
        cand = (score, -rd, -od)
        if cand > best:
            best = cand
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]