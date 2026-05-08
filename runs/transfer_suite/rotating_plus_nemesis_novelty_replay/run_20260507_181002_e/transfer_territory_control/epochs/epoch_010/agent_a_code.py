def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    try:
        sx, sy = int(sp[0]), int(sp[1])
    except:
        sx, sy = 0, 0
    try:
        ox, oy = int(op[0]), int(op[1])
    except:
        ox, oy = w - 1, h - 1

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            try:
                obstacles.add((int(p[0]), int(p[1])))
            except:
                pass

    def tos(key):
        S = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                try:
                    S.add((int(p[0]), int(p[1])))
                except:
                    pass
        return S

    resources = tos("resources")
    unclaimed = tos("unclaimed_cells")
    selfT = tos("self_territory")
    oppT = tos("opponent_territory")

    if not unclaimed and resources:
        unclaimed = set(resources)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = list(resources) if resources else list(unclaimed)
    best = (float("-inf"), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        dist = md((nx, ny), (ox, oy))
        if targets:
            d0 = min(md(cell, t) for t in targets)
        else:
            d0 = 0
        score = 0
        if cell in resources:
            score += 100000
        if cell in unclaimed:
            score += 5000
        if cell in selfT:
            score += 500
        if cell in oppT:
            score -= 2000
        score += max(0, (w + h) - d0) * 5
        if dist <= 1 and cell in unclaimed:
            score += 250
        if score > best[0]:
            best = (score, dx, dy)

    if best[0] == float("-inf"):
        return [0, 0]
    return [best[1], best[2]]