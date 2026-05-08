def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_adv(px, py):
        if not resources:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            return -cheb(px, py, tx, ty)
        best = -10**30
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < do:
                sc = (do - ds) * 100 - ds  # strongly prefer reachable-first
            else:
                sc = -(ds - do) * 5 - ds   # still prefer smaller ds if contested
            if sc > best:
                best = sc
        return best

    # If currently on a resource, still choose move that keeps us best (could be irrelevant but deterministic).
    best_move = [0, 0]
    best_val = -10**30
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = best_adv(nx, ny)
        # Small tie-break: move that also reduces our cheb distance to the best resource
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move