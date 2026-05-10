def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in (observation.get("self_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    opT = set()
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))

    unT = []
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unT.append((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    tx, ty = ox, oy
    bestd = None
    if unT:
        for x, y in unT:
            if (x, y) in opT:
                continue
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if bestd is None or d < bestd:
                bestd, tx, ty = d, x, y

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if (nx, ny) in opT:
            score = -10**12
        else:
            score = 0
            score += 5 if (nx, ny) in selfT else 0
            score += 20 if unT and (nx, ny) in set(unT) and (nx, ny) not in opT else 0
            score += -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
            score += -2 if dx == 0 and dy == 0 else 0
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]