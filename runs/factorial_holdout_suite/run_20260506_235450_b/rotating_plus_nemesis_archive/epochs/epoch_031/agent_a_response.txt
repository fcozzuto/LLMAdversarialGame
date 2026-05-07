def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = r[0], r[1]
            if (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # pick target maximizing immediate competitive advantage
        local_best = None
        for i, (tx, ty) in enumerate(resources):
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # higher is better: we prefer moves that increase being closer than opponent
            adv = d_opp - d_self
            # break ties by favoring nearer resource and a deterministic target index
            key = (adv, -d_self, -i)
            if local_best is None or key > local_best:
                local_best = key
        if best_key is None or local_best > best_key:
            best_key = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]