def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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
        targetx, targety = ox, oy
    else:
        bestd = None
        targetx, targety = resources[0]
        for x, y in resources:
            d = abs(sx - x) + abs(sy - y)
            if bestd is None or d < bestd:
                bestd = d
                targetx, targety = x, y

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestmv = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dt = abs(nx - targetx) + abs(ny - targety)
        do = abs(nx - ox) + abs(ny - oy)
        score = (dt * 1000) - do  # prefer closer to target, then farther from opponent
        if best is None or score < best:
            best = score
            bestmv = (dx, dy)

    return [int(bestmv[0]), int(bestmv[1])]