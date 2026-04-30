def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def cheb(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue
        mind = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if mind is None or d < mind:
                mind = d
        oppd = cheb(nx, ny, ox, oy)
        score = (-mind, -oppd, 0 if dx == 0 and dy == 0 else -1)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]