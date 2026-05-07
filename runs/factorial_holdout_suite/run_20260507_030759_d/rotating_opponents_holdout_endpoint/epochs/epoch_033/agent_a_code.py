def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)
    rem_cnt = observation.get("remaining_resource_count", len(resources))

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    # Strategy shift: time-aware contested targeting.
    # If time is tight, go nearest. Otherwise, prioritize resources where we are closer than opponent.
    tight = (turns_remaining <= (rem_cnt * 2 + 4))
    best = None
    best_key = None
    for x, y in res:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        if tight:
            key = (-sd, x, y)  # minimize sd
        else:
            adv = od - sd
            # maximize advantage; if negative, still pick best available, but prefer closer to us.
            key = (adv, -sd, -od, x, y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    moves.append((0, 0))

    # Choose deterministic best step: reduce our distance primarily; avoid making us closer for the opponent.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # od2 is constant (opponent doesn't move), but keep structure for clarity; tie-break uses board position.
        mkey = (-sd2, -abs(nx - ox) - abs(ny - oy), nx, ny)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]