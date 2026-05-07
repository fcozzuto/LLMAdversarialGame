def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set(obstacles_raw) if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # If standing adjacent diagonally, prefer collecting that resource directly.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in res and (inb(nx, ny) and (nx, ny) not in obstacles):
                return [dx, dy]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Score this next position by target competition: (opponent time - our time),
        # tie-break by sooner arrival and then deterministic position ordering.
        cur_best_adv = None
        cur_best_t = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if cur_best_adv is None or (adv, -ds, -rx, -ry) > (cur_best_adv, -cur_best_t, 0, 0):
                cur_best_adv = adv
                cur_best_t = ds

        # Add slight preference for moving toward the single best resource from current state
        # to prevent oscillation when adv is tied.
        base_adv = -10**9
        base_ds = 10**9
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if (adv, -ds, -rx, -ry) > (base_adv, -base_ds, 0, 0):
                base_adv = adv
                base_ds = ds

        key = (cur_best_adv, -cur_best_t, base_adv, -base_ds, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best