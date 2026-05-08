def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18
    best_t = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        mv = -10**18
        mt = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we can arrive not later than opponent; otherwise reduce their lead.
            val = (do - ds) * 1000 - ds
            if val > mv:
                mv = val
                mt = (rx, ry)
            elif val == mv and (mt is None or (rx, ry) < mt):
                mt = (rx, ry)

        if mv > best_val or (mv == best_val and (best_t is None or (mt is not None and mt < best_t))):
            best_val = mv
            best_move = (dx, dy)
            best_t = mt

    return [best_move[0], best_move[1]]