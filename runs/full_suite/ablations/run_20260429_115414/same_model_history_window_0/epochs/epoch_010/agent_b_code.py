def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    resources = [tuple(p) for p in observation.get('resources', [])]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx >= dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                # staying allowed; keep it as a candidate
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            d = cheb(nx, ny, tx, ty)
            v = -d
            if bestv is None or v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Deny resources: prefer moves that create the largest advantage (opp closer than us => bad)
    best = None
    bestv = None
    for dx, dy, nx, ny in moves:
        # Advantage defined as how much closer opponent is than us (negative is good for us being closer)
        # We maximize opponent_distance - self_distance (bigger means opponent farther or we closer).
        local_best = -10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer actions that also reduce our distance a bit.
            v = (od - sd) * 10 - sd
            if v > local_best:
                local_best = v
        if bestv is None or local_best > bestv:
            bestv, best = local_best, (dx, dy)

    return [best[0], best[1]]