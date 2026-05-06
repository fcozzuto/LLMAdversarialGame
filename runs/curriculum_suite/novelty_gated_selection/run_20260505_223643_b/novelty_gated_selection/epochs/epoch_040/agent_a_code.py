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

    def manh(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da + db

    # Pick a resource where we have the biggest deterministic reach advantage.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        oppd = manh(ox, oy, rx, ry)
        # Maximize (oppd - myd); tie-break: smaller myd, larger oppd (deny), then stable by coordinates.
        key = (-(oppd - myd), myd, -oppd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Evaluate next positions: avoid obstacles, advance to target, and keep away from opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            val = (10**9, 10**9)
        else:
            myd_next = manh(nx, ny, tx, ty)
            myd_now = manh(sx, sy, tx, ty)
            # Prefer getting closer; also prefer denying opponent by increasing their distance to target.
            oppd_next = manh(ox, oy, tx, ty)
            oppd_me = manh(nx, ny, ox, oy)
            # Penalize moving away from target; reward proximity to target and separation from opponent.
            val = (myd_next - myd_now, myd_next, -oppd_next, -oppd_me, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]