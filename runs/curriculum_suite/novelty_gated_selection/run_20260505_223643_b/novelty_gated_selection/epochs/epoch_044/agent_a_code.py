def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Prefer resources we can reach earlier; also deny opponent resources they are likely to reach.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        oppd = manh(ox, oy, rx, ry)
        # If tie, go to the one closer to us; otherwise prioritize deny (oppd - myd).
        key = (-(oppd - myd), myd, oppd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # If opponent is much closer to the chosen target, bias toward intercepting vicinity.
    myd0 = manh(sx, sy, tx, ty)
    oppd0 = manh(ox, oy, tx, ty)
    intercept_weight = 3 if oppd0 < myd0 else 1

    # Evaluate next positions with obstacle penalty and slight goal/deny shaping.
    best_mv = (0, 0)
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            sc = -10**9
        else:
            myd = manh(nx, ny, tx, ty)
            oppd = manh(ox, oy, tx, ty)
            # Primary: reduce our distance to target; Secondary: increase opponent remaining distance to target.
            sc = -myd * 10 + (oppd - oppd0) * 2
            # Intercept bias: move so that opponent's distance to our next is worse.
            sc += -(manh(ox, oy, nx, ny) - manh(ox, oy, sx, sy)) * intercept_weight
            # Minor preference to progress (avoid dithering).
            sc += - (abs(nx - tx) + abs(ny - ty)) * 0.5
        if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < best_mv):
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]