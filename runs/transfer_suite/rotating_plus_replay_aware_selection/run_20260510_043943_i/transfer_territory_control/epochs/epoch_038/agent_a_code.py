def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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
    target_list = resources if resources else [(ox, oy)]

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    best = None
    best_move = [0, 0]

    def best_dist(x, y):
        d = None
        for tx, ty in target_list:
            dd = abs(tx - x) + abs(ty - y)
            if d is None or dd < d:
                d = dd
        return d

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = best_dist(nx, ny)
            score = (d, abs(dx) + abs(dy))
            if best is None or score < best:
                best, best_move = score, [dx, dy]
    return [int(best_move[0]), int(best_move[1])]