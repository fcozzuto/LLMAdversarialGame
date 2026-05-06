def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    ob = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in ob

    res = observation.get("resources", []) or []
    targets = []
    for r in res:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                targets.append((x, y))

    def score_cell(x, y):
        d = abs(x - sx) + abs(y - sy)
        if not targets:
            return -abs(x - ox) - d
        best = min(abs(x - tx) + abs(y - ty) for tx, ty in targets) if targets else 10**9
        return -d + 2 * (-best)

    if targets:
        cx, cy = sx, sy
        best_move = (10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sc = score_cell(nx, ny)
            if sc < best_move[0]:
                best_move = (sc, dx, dy)
        return [best_move[1], best_move[2]]

    best_move = (10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        if -d < best_move[0]:
            best_move = (-d, dx, dy)
    return [best_move[1], best_move[2]]