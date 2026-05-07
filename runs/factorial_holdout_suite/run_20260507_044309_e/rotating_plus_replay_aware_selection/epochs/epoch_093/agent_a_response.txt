def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step_toward(tx, ty, x, y):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        nx, ny = x + dx, y + dy
        if legal(nx, ny):
            return [dx, dy]
        # deterministic fallback: axis first
        nx, ny = x + dx, y
        if legal(nx, ny):
            return [dx, 0]
        nx, ny = x, y + dy
        if legal(nx, ny):
            return [0, dy]
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = w // 2, h // 2
        return step_toward(tx, ty, sx, sy)

    # Choose a resource where we are relatively ahead; if none, choose the one with smallest opp lead.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        ahead = do - ds
        key = (-(ahead), ds, -do, rx, ry)  # minimize negative ahead => maximize ahead
        # But ensure preference to having any positive ahead; deterministic by the same key.
        if best is None or (ahead > (best[2] if best else -10**9)) or (ahead == (best[2] if best else None) and key < best[0]):
            best = (key, (rx, ry), ahead)
    tx, ty = best[1]

    # One-ply move selection to reduce distance to target while staying legal.
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; tie-break by keeping opponent not closer than us.
        lead_after = do - d
        key = (-lead_after, d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move