def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    # Pick target we are most likely to secure: maximize our advantage, then prefer nearer/safer cells.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        ahead = 1 if sd < od else 0
        # Prefer: strictly ahead, smaller sd, larger (od-sd), and avoid "edge-ish" late targets slightly.
        key = (ahead, -(sd), (od - sd), -rx - ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_step = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Score by progress toward target and keeping opponent from being closer.
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        ahead = 1 if d_self < d_opp else 0
        # If not strictly ahead, still prefer reducing our distance sharply.
        score = (ahead, -d_self, d_opp - d_self, -abs(nx - tx) - abs(ny - ty), -abs(nx - sx) - abs(ny - sy))
        if best_score is None or score > best_score:
            best_score = score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]