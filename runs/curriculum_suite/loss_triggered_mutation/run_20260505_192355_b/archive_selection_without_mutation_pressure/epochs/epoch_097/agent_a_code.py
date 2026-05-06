def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def clamp(x, a, b):
        return a if x < a else b if x > b else x

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Obstacle proximity penalty (discourage routes that keep you near blocks)
        prox = 0
        for ox2, oy2 in ((nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1), (nx+1, ny+1), (nx-1, ny-1), (nx+1, ny-1), (nx-1, ny+1)):
            if (ox2, oy2) in obstacles:
                prox += 1

        # Maximize our advantage after the move; also push toward resources that are contested
        best_cell = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Advantage: positive means opponent farther than us (good)
            adv = od - sd
            # If we can grab soon, strongly prefer it; if opponent is closer, still consider blocking routes.
            soon = 20 if sd <= 1 else 0
            # Slight preference for reducing absolute distance; favors progress while keeping contest advantage.
            cell = adv * 10 + soon - sd - prox * 2
            if cell > best_cell:
                best_cell = cell

        # Tie-break: prefer closer to best resource among moves deterministically
        # by also considering our minimum distance to any resource.
        min_sd = min(md(nx, ny, rx, ry) for rx, ry in resources)
        score = best_cell * 100 - min_sd
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move