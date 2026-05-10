def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except Exception:
        sx, sy, ox, oy = 0, 0, 0, 0
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    un = observation.get("unclaimed_cells") or []
    targets = []
    for p in un:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))
    if not targets:
        res = observation.get("resources") or []
        for p in res:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if targets:
        tx, ty = min(targets, key=lambda p: dist(sx, sy, p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = (0, 0)
    bestv = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = -dist(nx, ny, tx, ty)
        if (nx, ny) == (ox, oy):
            v += 10**6
        if dx == 0 and dy == 0:
            v -= 1
        if v > bestv:
            bestv = v
            best = [dx, dy]
    if bestv == -10**9:
        best = [0, 0]
    return best