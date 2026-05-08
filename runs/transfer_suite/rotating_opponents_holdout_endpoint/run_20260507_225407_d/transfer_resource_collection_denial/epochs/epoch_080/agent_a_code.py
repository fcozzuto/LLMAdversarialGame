def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        if (rx, ry) in obstacles:
            continue
        # Prefer resources we can reach earlier; if close, deny opponent by favoring larger (do - ds)
        score = ds - 0.85 * (do - ds)
        # Minor deterministic tie-breaker
        tie = (rx + ry, rx, ry)
        key = (score, tie)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    _, (tx, ty) = best
    curd = md(sx, sy, tx, ty)
    best_step = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        nd = md(nx, ny, tx, ty)
        # Prefer strictly better, otherwise minimal distance; deterministic tie by dx,dy order
        cand = (nd, -0.01 * (do if False else 0), dx * 10 + dy)
        # do placeholder removed by cand; keep deterministic ordering only
        if best_step is None or cand < best_step[0] or (nd == curd and best_step[0] > cand):
            best_step = (cand, (dx, dy))
    return [int(best_step[1][0]), int(best_step[1][1])]