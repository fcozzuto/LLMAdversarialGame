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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            d = max(abs(rx - sx), abs(ry - sy))
            if best is None or d < best:
                best = d
                target = (rx, ry)
    if target is None:
        best_score = None
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dist = max(abs(nx - ox), abs(ny - oy))
            score = dist
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    tx, ty = target
    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = max(abs(nx - tx), abs(ny - ty))
        d_opp = max(abs(nx - ox), abs(ny - oy))
        score = (-d_self) + (0.05 * d_opp)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move if best_score is not None else [0, 0]