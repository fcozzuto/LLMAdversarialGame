def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)  # maximize separation
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    # Pick a target resource that we can reach relatively earlier.
    best_t = None
    best_score = -10**9
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not cell_ok(tx, ty):
            continue
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        rel = do - ds  # positive means we're closer
        # Prefer also overall closeness so we don't chase too-far relative wins.
        score = rel * 10 - ds
        # Deterministic tie-break
        if score > best_score or (score == best_score and (tx, ty) < best_t):
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t if best_t is not None else (sx, sy)

    # One-step greedy: minimize our distance while also discouraging giving the opponent access.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        ds1 = cheb(nx, ny, tx, ty)
        do1 = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        # If we can arrive immediately, take it.
        arrive = 50 if (nx, ny) == (tx, ty) else 0
        # Improve relative advantage; also avoid moving into likely contested regions by staying closer than opponent.
        val = arrive + (do1 - ds1) * 10 - ds1
        # Small deterministic preference: closer to target, then towards increasing x then y
        if (nx == sx and ny == sy):
            val -= 1  # prefer moving if equal quality
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move