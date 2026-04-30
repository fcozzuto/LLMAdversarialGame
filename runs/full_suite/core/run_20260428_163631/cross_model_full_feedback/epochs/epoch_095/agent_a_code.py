def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal_moves(x, y):
        moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    moves.append((dx, dy))
        return moves

    moves = legal_moves(sx, sy)
    if not moves:
        return [0, 0]

    oppd = abs(sx - ox) + abs(sy - oy)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if resources:
            dmin = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            dmin = abs(nx - cx) + abs(ny - cy)
        nd = abs(nx - ox) + abs(ny - oy)
        key = (dmin, -nd, dx, dy)  # nearest resource, maximize distance, deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    # If tied close to opponent, bias to stay or move away deterministically
    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]