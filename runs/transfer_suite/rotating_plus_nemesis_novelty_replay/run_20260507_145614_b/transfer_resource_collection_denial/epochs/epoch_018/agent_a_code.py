def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        tx = min(max(tx, 0), w - 1)
        ty = min(max(ty, 0), h - 1)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best_val:
                best_val = d
                best = [dx, dy]
        return best if best is not None else [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Choose the best resource assuming we aim to collect it next.
        # Value favors being closer than opponent; tie-break favors shorter own distance.
        local_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer (good)
            val = (adv * 100) - ds  # strong deterrent against resources opponent can reach first
            if val > local_best:
                local_best = val
        # Small preference to continue toward the current best resource direction deterministically
        if local_best > best_val:
            best_val = local_best
            best = [dx, dy]
    return best if best is not None else [0, 0]