def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_score = -10**18
    best_move = (0, 0)

    # One-step lookahead: pick move that best swings contested resource lead (denial/interception).
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            nx, ny = sx, sy
            if not valid(nx, ny):
                nx, ny = sx, sy

        local_best = -10**18
        for tx, ty in resources:
            ds2 = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            lead = do - ds2  # positive => we get there first
            # Emphasize denied targets: if opponent is not much slower, prioritize.
            contested = 1 if do <= ds2 + 1 else 0
            # Also prefer closer goals to reduce tail latency.
            val = lead * 200 - ds2 * 5 + contested * 60 - abs(tx - nx) * 0 + abs(ty - ny) * 0
            # Small deterministic tie-break: favor resources with smaller coords when nearly tied.
            if do - ds2 == lead and ds2 == ds2:
                val += -(tx * 0.01 + ty * 0.001)
            if val > local_best:
                local_best = val

        if local_best > best_score:
            best_score = local_best
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]