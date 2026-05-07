def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    res = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not res:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    for r in res:
        rx, ry = r[0], r[1]
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer smaller (myd - opd): reach earlier than opponent.
        # Tie-break toward closer and toward lexicographically smaller resource.
        key = (myd - opd, myd, -opd, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    best_move = (None, None)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = man(nx, ny, tx, ty)
        opd2 = man(ox, oy, tx, ty)
        # Prefer reducing distance; keep opponent as far as possible; deterministic tie-break.
        key = (myd2, -(opd2 - myd2), dx, dy, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [best_move[0], best_move[1]]