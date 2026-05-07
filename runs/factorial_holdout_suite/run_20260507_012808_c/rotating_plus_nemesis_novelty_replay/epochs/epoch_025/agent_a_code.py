def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d(a, b, c, d2):
        dx = a - c
        dy = b - d2
        return dx * dx + dy * dy

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            val = d(sx, sy, rx, ry)
            if best is None or val < best:
                best = val
                target = (rx, ry)

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if target is None:
            score = d(nx, ny, ox, oy)  # go farther from opponent
            score = -score
        else:
            score = -d(nx, ny, target[0], target[1])  # closer to resource
            score = score * 1000000 - d(nx, ny, ox, oy)  # also prefer farther from opponent
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if inb(sx, sy):
        return list(best_move)
    # Fallback: choose any valid move deterministically
    for dx, dy in moves:
        if inb(sx + dx, sy + dy):
            return [dx, dy]
    return [0, 0]