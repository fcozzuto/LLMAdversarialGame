def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                if 0 <= x < w and 0 <= y < h:
                    obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res = observation.get("resources") or []
    targets = []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                targets.append((x, y))
        elif isinstance(p, dict) and "x" in p and "y" in p:
            x, y = p.get("x"), p.get("y")
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                targets.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = None

    def score(nx, ny):
        dself = abs(nx - sx) + abs(ny - sy)
        dopp = abs(nx - ox) + abs(ny - oy)
        tgt = 0
        if targets:
            tgt = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        else:
            tgt = abs(nx - w // 2) + abs(ny - h // 2)
        return (tgt, -dopp, dself)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score(nx, ny)
        if best is None or sc < best_score:
            best = [dx, dy]
            best_score = sc

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                return [dx, dy]
        return [0, 0]
    return best