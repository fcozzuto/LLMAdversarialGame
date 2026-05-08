def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    resources = observation.get("resources", []) or []
    target = None
    bestd = 10**18
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                d = dist(sx, sy, x, y)
                if d < bestd:
                    bestd = d
                    target = (x, y)

    if target is None:
        unclaimed = observation.get("unclaimed_cells", []) or []
        bestd = 10**18
        for u in unclaimed:
            if isinstance(u, (list, tuple)) and len(u) >= 2:
                x, y = u[0], u[1]
                if inb(x, y):
                    d = dist(sx, sy, x, y)
                    if d < bestd:
                        bestd = d
                        target = (x, y)

    if target is None:
        target = (ox, oy)

    tx, ty = target
    cur_to_target = dist(sx, sy, tx, ty)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist(nx, ny, tx, ty)
        oppd = dist(nx, ny, ox, oy)
        score = (cur_to_target - d) * 10 + oppd * 0.001
        if (nx, ny) == target:
            score += 1000
        candidates.append((score, -oppd, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][2]), int(candidates[0][3])]