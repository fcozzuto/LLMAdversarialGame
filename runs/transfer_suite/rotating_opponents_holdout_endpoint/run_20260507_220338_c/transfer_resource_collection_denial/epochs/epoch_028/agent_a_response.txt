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

    def pick_target():
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = manh(sx, sy, rx, ry)
            opd = manh(ox, oy, rx, ry)
            key = (opd - myd, -(myd + opd), -(rx + ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best if best is not None else tuple(resources[0])

    tx, ty = pick_target()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_k = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = manh(nx, ny, tx, ty)
        # Also reward moves that reduce opponent ability to contest near the same target
        opd = manh(ox, oy, tx, ty)
        # Prefer minimizing our distance; if tied, prefer decreasing (opd-myd)
        k = (-myd, (opd - myd), -(abs(tx - nx) + abs(ty - ny)))
        if best_k is None or k > best_k:
            best_k = k
            best_m = (dx, dy)

    # If all candidate moves were blocked, stay.
    return [int(best_m[0]), int(best_m[1])]