def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    tr = observation.get("turns_remaining", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def resource_priority(rx, ry):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach, and where we are at least not behind.
        reachable = 1 if ds <= tr else 0
        margin = do - ds  # positive => we are earlier
        behind_pen = -1000000 if reachable == 0 else 0
        # If opponent is earlier, strongly penalize; if we are earlier, reward by margin.
        return behind_pen + (0 if margin >= 0 else (-10000 - 10 * (-margin))) + 2 * ds - 3 * margin

    target = None
    best = 10**18
    for rx, ry in resources:
        if inb(rx, ry):
            p = resource_priority(rx, ry)
            if p < best or (p == best and (target is None or (rx, ry) < target)):
                best = p
                target = (rx, ry)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if target is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = target

    # If we are already at a good resource, avoid moving away unnecessarily.
    if cheb(sx, sy, tx, ty) == 0:
        return [0, 0]

    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        reachable = 1 if ds <= tr else 0
        margin = do - ds
        val = (0 if reachable else 1000000) + (0 if margin >= 0 else (50000 + 10 * (-margin))) + 3 * ds - 2 * margin
        # Slightly prefer moves that reduce opponent's distance to our current target less.
        if val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]