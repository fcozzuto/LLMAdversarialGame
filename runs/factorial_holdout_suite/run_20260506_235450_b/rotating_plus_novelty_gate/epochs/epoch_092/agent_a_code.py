def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                rs.append((x, y))
    if not rs:
        return [0, 0]

    best_t = rs[0]
    best_key = (-10**9, -10**9)
    for tx, ty in rs:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # prefer resources where we are ahead; small additional preference for nearer targets
        key = (do - ds, -(ds + ds // 2))
        if key > best_key:
            best_key = key
            best_t = (tx, ty)
    tx, ty = best_t

    # choose move that reduces distance to target; discourage stepping into/near opponent
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = (-10**9, -10**9, -10**9)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(nx, ny, ox, oy)
        # primary: minimize distance to target (encode as negative)
        # secondary: keep opponent farther (larger oppd)
        # tertiary: deterministic preference ordering by dx,dy via encoded score
        score = (-myd, oppd, -abs(dx) - abs(dy))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]