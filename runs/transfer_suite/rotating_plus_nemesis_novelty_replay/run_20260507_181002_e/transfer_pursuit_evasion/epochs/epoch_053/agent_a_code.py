def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    if res:
        tx, ty = min(res, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = (ox, oy) if not evader else (sx, sy)

    best = None
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = md(nx, ny, tx, ty)
        score = d if evader else -d
        if best is None or score > best:
            best = score
            bestd = (dx, dy)
        elif best is not None and score == best:
            if (dx, dy) < bestd:
                bestd = (dx, dy)

    if bestd is not None:
        return [bestd[0], bestd[1]]

    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            return [dx, dy]
    return [0, 0]