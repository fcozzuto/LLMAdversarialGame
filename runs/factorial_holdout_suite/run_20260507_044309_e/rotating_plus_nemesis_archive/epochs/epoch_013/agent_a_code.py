def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (-(abs(sx-ox)+abs(sy-oy)), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                v = -(abs(nx-ox) + abs(ny-oy))
                if v > best[0]:
                    best = (v, dx, dy)
        return [best[1], best[2]]

    best_v = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        self_d = abs(nx - ox) + abs(ny - oy)
        # choose the resource where we have the largest "tempo advantage" over opponent
        v = -self_d * 0.05
        for rx, ry in resources:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we are closer to; strongly avoid cells where opponent likely contests.
            tempo = (od - sd)  # higher is better
            # Prefer closer targets among those with positive tempo
            v += tempo * 2.0 - sd * 0.15
        # Small deterministic tie-break: prefer moves that reduce own distance to nearest resource
        mind = min(abs(rx - nx) + abs(ry - ny) for rx, ry in resources)
        v -= mind * 0.01
        if v > best_v:
            best_v = v
            best_move = [dx, dy]
    return best_move