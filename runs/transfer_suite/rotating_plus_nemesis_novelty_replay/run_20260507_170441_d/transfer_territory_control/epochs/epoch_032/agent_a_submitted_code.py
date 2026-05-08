def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    moves = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    target = None
    res = observation.get("resources") or []
    best = None
    for r in res:
        try:
            x, y = int(r[0]), int(r[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
            d = abs(x - sx) + abs(y - sy)
            if best is None or d < best:
                best = d
                target = (x, y)
    if target is None:
        unclaimed = observation.get("unclaimed_cells") or []
        best = None
        for u in unclaimed:
            try:
                x, y = int(u[0]), int(u[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                d = abs(x - sx) + abs(y - sy)
                if best is None or d < best:
                    best = d
                    target = (x, y)
    if target is None:
        target = (w // 2, h // 2)

    px = target[0] - sx
    py = target[1] - sy
    desired = []
    if px < 0:
        desired.append((-1, 0))
    elif px > 0:
        desired.append((1, 0))
    if py < 0:
        desired.append((0, -1))
    elif py > 0:
        desired.append((0, 1))
    desired += moves

    best_move = None
    best_score = None
    for dx, dy in desired:
        if (dx, dy) not in legal:
            continue
        nx, ny = sx + dx, sy + dy
        score = abs(target[0] - nx) + abs(target[1] - ny)
        # small bias to move away from opponent if tied
        score = (score * 10) - (abs(nx - ox) + abs(ny - oy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is not None:
        return [int(best_move[0]), int(best_move[1])]

    # fallback: first legal move in deterministic order (up, right, down, left, diag, stay)
    order = [(0, -1), (1, 0), (0, 1), (-1, 0),
             (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    for dx, dy in order:
        if (dx, dy) in legal:
            return [int(dx), int(dy)]
    return [0, 0]