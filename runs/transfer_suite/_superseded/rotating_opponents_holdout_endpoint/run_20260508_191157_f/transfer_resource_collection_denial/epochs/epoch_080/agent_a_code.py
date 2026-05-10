def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda c: (md(sx, sy, c[0], c[1]), c[0] * 9 + c[1]))
        best = (0, 0, 10**9, 10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if (d, nx, ny) < (best[2], best[0], best[1]):
                best = (dx, dy, d, nx * 9 + ny)
        return [int(best[0]), int(best[1])]

    # Score moves by best "win-next-resource" advantage they enable.
    bestMove = (0, 0)
    bestKey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # For each resource, estimate whether next position beats opponent at that resource.
        bestResKey = None
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            gain = opd - myd  # positive => we are closer
            # Prefer positive gain, then smallest my distance, then deterministic coord
            k = (-(1 if gain > 0 else 0), -gain, myd, rx, ry)
            if bestResKey is None or k < bestResKey:
                bestResKey = k
        # Additional tie-break: don't drift into worst corners near opponent (lightly)
        oppd = md(nx, ny, ox, oy)
        moveKey = (bestResKey, oppd, nx, ny)
        if bestKey is None or moveKey < bestKey:
            bestKey = moveKey
            bestMove = (dx, dy)

    return [int(bestMove[0]), int(bestMove[1])]