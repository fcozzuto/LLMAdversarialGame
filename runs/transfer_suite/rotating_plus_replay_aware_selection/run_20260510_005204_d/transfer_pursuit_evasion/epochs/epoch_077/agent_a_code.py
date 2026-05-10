def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "")).lower()
    evader = ("evader" in role) or ("runner" in role) or ("evade" in role)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if (not evader) and resources:
        best = None
        bestd = 10**18
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if (rx, ry) in blocked:
                    continue
                d = dist2(sx, sy, rx, ry)
                if d < bestd:
                    bestd = d
                    best = (rx, ry)
        if best is None:
            bestx, besty = (w // 2, h // 2)
        else:
            bestx, besty = best
        bestmove = None
        bestmv = 10**18
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = dist2(nx, ny, bestx, besty)
            if d < bestmv or (d == bestmv and (bestmove is None or (dx, dy) < bestmove)):
                bestmv = d
                bestmove = (dx, dy)
        return [int(bestmove[0]), int(bestmove[1])]

    tx, ty = (ox, oy) if (ox or oy) else (w // 2, h // 2)
    if evader:
        far = -1
        bestmove = (0, 0)
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = dist2(nx, ny, tx, ty)
            if d > far or (d == far and (dx, dy) < bestmove):
                far = d
                bestmove = (dx, dy)
        return [int(bestmove[0]), int(bestmove[1])]

    cx, cy = w // 2, h // 2
    bestmove = (0, 0)
    bestmv = 10**18
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d = dist2(nx, ny, cx, cy)
        if d < bestmv or (d == bestmv and (dx, dy) < bestmove):
            bestmv = d
            bestmove = (dx, dy)
    return [int(bestmove[0]), int(bestmove[1])]