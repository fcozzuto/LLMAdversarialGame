def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in dirs:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    targets = resources if resources else [(w // 2, h // 2), (0, h // 2), (w - 1, h // 2), (w // 2, 0), (w // 2, h - 1)]
    best = (10**18, 10**18, 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        myd = min(cheb(nx, ny, tx, ty) for (tx, ty) in targets)
        opd = min(cheb(ox, oy, tx, ty) for (tx, ty) in targets)

        # Prefer moves that reduce my distance to a resource, and (slightly) increase opponent disadvantage.
        # Small tie-breakers: keep movement cost low then deterministic direction order.
        score1 = myd - (0.2 * opd)
        score2 = cheb(nx, ny, sx, sy)  # 0 for stay, 1 for adj (diagonal also 1 in cheb)
        cand = (score1, score2, dirs.index((dx, dy)), dx, dy)
        if cand < best:
            best = cand

    return [best[3], best[4]]