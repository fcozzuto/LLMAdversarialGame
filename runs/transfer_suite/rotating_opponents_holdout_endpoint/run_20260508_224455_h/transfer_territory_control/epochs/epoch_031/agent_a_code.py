def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    opp_ter = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    nbrs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    if unclaimed:
        best = None
        bestv = None
        for ux, uy in unclaimed:
            dcent = abs(ux - cx) + abs(uy - cy)
            dadv = min(abs(ux - tx) + abs(uy - ty) for tx, ty in opp_ter) if opp_ter else 999
            v = (-(dcent), (0 if dadv == 0 else -dadv))
            key = (v[0], v[1])
            if best is None or key > bestv:
                bestv = key
                best = (ux, uy)
        tx, ty = best
    else:
        tx, ty = ox, oy

    if (sx, sy) == (tx, ty):
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_score = None
    for dx, dy in nbrs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        adj = 0
        if opp_ter:
            for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if (nx + adx, ny + ady) in opp_ter:
                    adj = 1
                    break
        score = (-d, adj, -abs(nx - cx) - abs(ny - cy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    nx, ny = sx + best_move[0], sy + best_move[1]
    if not inb(nx, ny) or blocked(nx, ny):
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]