def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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
    if not resources:
        resources = [(w // 2, h // 2)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick best resource we are at least as close to as opponent (if possible), else closest overall
    best = None
    best_key = None
    for rx, ry in resources:
        d1 = man(sx, sy, rx, ry)
        d2 = man(ox, oy, rx, ry)
        key = (d2 <= d1, d2 - d1, -d1)  # prefer secure, then biggest lead, then nearer
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    rx, ry = best

    # Choose move that reduces our distance to target; break ties by increasing opponent distance
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_our = man(nx, ny, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        score = (-d_our, d_opp, abs(dx) + abs(dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if not inside(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]