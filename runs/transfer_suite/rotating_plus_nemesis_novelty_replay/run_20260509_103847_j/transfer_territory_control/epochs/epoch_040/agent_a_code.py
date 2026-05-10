def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    unT = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.append((x, y))

    opT = []
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opT.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    candidates = unT
    if not candidates and opT:
        t = opT[0]
        candidates = [p for p in [(t[0] + dx, t[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)] if 0 <= p[0] < w and 0 <= p[1] < h and p not in obstacles and p not in selfT]

    if not candidates:
        target = (cx, cy)
    else:
        best = None
        bestd = None
        for x, y in candidates:
            if (x, y) in selfT:
                continue
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if best is None or d < bestd or (d == bestd and (x, y) < best):
                best, bestd = (x, y), d
        target = best if best is not None else (cx, cy)

    tx, ty = target
    stepx = tx - sx
    stepy = ty - sy
    dx = 1 if stepx > 0 else (-1 if stepx < 0 else 0)
    dy = 1 if stepy > 0 else (-1 if stepy < 0 else 0)

    nx, ny = sx + dx, sy + dy
    if (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles):
        return [dx, dy]

    bestdir = None
    bestscore = None
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny) + (1 if (nx, ny) in selfT else 0)
        if bestdir is None or score < bestscore:
            bestdir, bestscore = (ddx, ddy), score
    return [bestdir[0], bestdir[1]] if bestdir is not None else [0, 0]