def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p[:2]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    unclaimed = [tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    resources = [tuple(p[:2]) for p in (observation.get("resources") or []) if p and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    target = None
    if unclaimed:
        best = None
        best_key = None
        for x, y in unclaimed:
            if not inb(x, y):
                continue
            d = abs(x - sx) + abs(y - sy)
            k = (d, abs(x - ox) + abs(y - oy), x, y)
            if best_key is None or k < best_key:
                best_key = k
                best = (x, y)
        target = best
    if target is None:
        pool = resources if resources else [(ox, oy)]
        best = None
        best_key = None
        for x, y in pool:
            if not inb(x, y):
                continue
            d = abs(x - sx) + abs(y - sy)
            k = (d, x, y)
            if best_key is None or k < best_key:
                best_key = k
                best = (x, y)
        target = best if best is not None else (sx, sy)

    tx, ty = target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cur = abs(nx - tx) + abs(ny - ty)
        oppd = abs(nx - ox) + abs(ny - oy)
        score = (cur, -oppd, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]