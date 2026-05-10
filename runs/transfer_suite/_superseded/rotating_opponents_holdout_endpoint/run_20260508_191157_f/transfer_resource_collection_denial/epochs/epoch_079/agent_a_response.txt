def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    if not resources:
        tx, ty = min(corners, key=lambda c: (md(sx, sy, c[0], c[1]), c[0] * 9 + c[1]))
        best = (0, 0, 10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if (d, -nx, -ny) < (best[2], best[0], best[1]):
                best = (dx, dy, d)
        return [int(best[0]), int(best[1])]

    # Target resources we can beat: maximize (opponent_dist - my_dist), then minimize my_dist, then deterministic tie on coord.
    bestR = None
    bestKey = None
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        key = (-(opd - myd), myd, rx * 9 + ry)  # lower is better; first means larger advantage
        if bestKey is None or key < bestKey:
            bestKey = key
            bestR = (rx, ry)

    tx, ty = bestR
    bestMove = (0, 0)
    bestScore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd1 = md(nx, ny, tx, ty)
        # Also consider keeping/ increasing opponent distance to the same target to discourage giving it away.
        opd1 = md(ox, oy, tx, ty)
        # Prefer moves that reduce my distance; small penalty for moving away; deterministic tie by coord.
        score = (myd1, -opd1, (nx - sx) * 10 + (ny - sy))
        if bestScore is None or score < bestScore:
            bestScore = score
            bestMove = (dx, dy)

    return [int(bestMove[0]), int(bestMove[1])]