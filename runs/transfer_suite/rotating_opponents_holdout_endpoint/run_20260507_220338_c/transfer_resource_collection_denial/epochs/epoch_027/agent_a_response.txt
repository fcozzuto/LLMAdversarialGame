def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick best resource by relative advantage (opponent closer is bad for us)
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # Prefer: larger (opd-myd), then smaller combined distance, then closer resource to us
        key = (opd - myd, -(myd + opd), -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        best = tuple(resources[0])
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_move_key = None

    myd_now = manh(sx, sy, tx, ty)
    opd_now = manh(ox, oy, tx, ty)
    denier = 1 if (opd_now + 1 < myd_now) else 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = manh(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # If opponent is threatening this target, prioritize cutting their advantage by moving to lower our distance fast.
        # Otherwise, keep maximizing our relative closeness.
        rel = opd - myd
        key = (rel, -(myd + opd), -abs((tx - nx)) - abs((ty - ny)), denier * (myd_now - myd))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]