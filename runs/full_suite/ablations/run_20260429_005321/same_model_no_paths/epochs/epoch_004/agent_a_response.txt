def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def blocked(x, y):
        return (x, y) in obstacles

    def adj_obstacle_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 3
        return pen

    def inside_score(x, y):
        if not inside(x, y) or blocked(x, y):
            return -10**12
        return -adj_obstacle_pen(x, y)

    # Choose a target resource where we can most improve our advantage vs the opponent.
    tx, ty = (w // 2), (h // 2)
    if resources:
        best = None
        for rx, ry in resources:
            myd = manh(sx, sy, rx, ry)
            opd = manh(ox, oy, rx, ry)
            # Prefer resources where opponent is relatively far; if close, prefer those nearer to us.
            key = (-(opd - myd), myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        base = inside_score(nx, ny)
        if base < -10**11:
            continue
        # Two-ply-ish heuristic: maximize our decrease to target, while not moving into risky squares.
        myd_now = manh(sx, sy, tx, ty)
        myd_next = manh(nx, ny, tx, ty)
        # Opponent distance fixed this turn; encode our "advantage improvement".
        opd = manh(ox, oy, tx, ty)
        adv_now = opd - myd_now
        adv_next = opd - myd_next
        key = (-adv_next, myd_next, adj_obstacle_pen(nx, ny), nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is not None:
        return best_move
    return [0, 0]