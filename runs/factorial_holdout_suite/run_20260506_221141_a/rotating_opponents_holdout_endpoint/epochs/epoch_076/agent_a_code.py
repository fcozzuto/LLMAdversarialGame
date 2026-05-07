def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    resources.append((x, y))

    if not resources or (sx, sy) in resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_rx = best_ry = None
    best_key = None
    for rx, ry in resources:
        d_ours = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        score = d_opp - d_ours  # prefer resources where we are relatively closer
        # tie-break: prefer smaller our distance, then prefer larger y, then smaller x (deterministic)
        key = (-score, d_ours, -ry, rx)
        if best_key is None or key < best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry
    # candidate moves: greedy toward target, but avoid obstacles if possible
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # order by tendency toward target
    dx_t = 0 if tx == sx else (1 if tx > sx else -1)
    dy_t = 0 if ty == sy else (1 if ty > sy else -1)
    def toward_key(m):
        mx, my = m
        # higher means more aligned with target direction
        return -(abs(mx - dx_t) + abs(my - dy_t), mx, my)

    candidates = []
    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((mx, my))
    if not candidates:
        return [0, 0]

    # Local objective: maximize (opp_dist - our_dist) after the move; tie-break stable
    best_m = None
    best_mkey = None
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        d_ours = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        score = d_opp - d_ours
        mkey = (-score, d_ours, -ny, nx)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_m = (mx, my)

    return [int(best_m[0]), int(best_m[1])]