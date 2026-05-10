def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    res_cells = []
    for p in resources:
        try:
            x, y = p
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                res_cells.append((x, y))
        except:
            pass

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                return [dx, dy]
        return [0, 0]

    target = None
    best = None
    for rx, ry in res_cells:
        d = man(sx, sy, rx, ry)
        if best is None or d < best:
            best = d
            target = (rx, ry)

    best_score = None
    best_move = (0, 0)
    for dx, dy, nx, ny in candidates:
        d_opp = man(nx, ny, ox, oy)
        d_res = man(nx, ny, target[0], target[1]) if target else 0
        score = 2 * d_opp - (d_res if target else 0)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]