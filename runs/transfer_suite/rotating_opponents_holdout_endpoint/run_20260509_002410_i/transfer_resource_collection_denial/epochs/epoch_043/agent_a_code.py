def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    # Pick a target we can reach earlier than opponent; otherwise the best "next race win".
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Encourage larger race lead; slight preference for closer cells.
        key = (opd - myd, -myd, -((rx - sx) ** 2 + (ry - sy) ** 2))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0
    if rx > sx:
        dx = 1
    elif rx < sx:
        dx = -1
    dy = 0
    if ry > sy:
        dy = 1
    elif ry < sy:
        dy = -1

    # Evaluate possible single-step moves (including staying), avoid obstacles.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Primary: get closer to target; Secondary: prefer matching dx/dy direction; Tertiary: avoid moving away.
        dist = cheb(nx, ny, rx, ry)
        dir_match = -((dx - mx) ** 2 + (dy - my) ** 2)
        candidates.append((dist, dir_match, abs(mx) + abs(my)))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], -t[1], t[2]))
    mx, my = moves[0]
    # Pick best deterministically
    bestm = None
    bestscore = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, rx, ry)
        dir_match = -((dx - mx) ** 2 + (dy - my) ** 2)
        score = (dist, -dir_match, abs(mx) + abs(my), mx, my)
        if bestscore is None or score < bestscore:
            bestscore = score
            bestm = (mx, my)
    return [int(bestm[0]), int(bestm[1])]