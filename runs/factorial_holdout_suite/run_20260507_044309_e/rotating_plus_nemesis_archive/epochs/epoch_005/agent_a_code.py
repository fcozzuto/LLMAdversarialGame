def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate position by best reachable resource advantage.
        local_best = None
        for tx, ty in resources:
            myd = manh(nx, ny, tx, ty)
            opd = manh(ox, oy, tx, ty)
            # Large weight on winning race; small penalty for distance; slight tie-break by opponent being farther.
            val = (opd - myd) * 10000 - myd * 10 - manh(sx, sy, tx, ty)
            if local_best is None or val > local_best:
                local_best = val

        # Prefer immediate collection if possible (myd=0 will be highest via val but reinforce deterministically)
        if local_best is None:
            continue
        if best_val is None or local_best > best_val or (local_best == best_val and (dx, dy) < best_move):
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]