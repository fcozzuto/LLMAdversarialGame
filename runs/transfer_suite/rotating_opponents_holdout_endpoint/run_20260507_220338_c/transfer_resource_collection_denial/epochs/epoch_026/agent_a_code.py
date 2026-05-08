def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_target():
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            key = (opd - myd, -(myd + opd), -(rx + ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best if best is not None else tuple(resources[0])

    tx, ty = best_target()
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    myd_now = md(sx, sy, tx, ty)
    opd_now = md(ox, oy, tx, ty)
    denier = 1 if opd_now + 1 < myd_now else 0

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)

        # If denier mode, prefer moves that increase opponent distance to the chosen resource
        # (shadow archetype tends to contest; we maximize our lead or create denies).
        deny_score = 0
        if denier:
            # approximate: if our move toward the resource reduces contest, reward it less and
            # reward increasing our distance to let opponent have to chase later (deterministic).
            deny_score = (myd - myd_now) * 2

        # Primary: minimize our distance; Secondary: maximize opponent advantage gap against next step
        gap = (opd - myd)
        score = (gap, -myd, deny_score, -(nx + ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move