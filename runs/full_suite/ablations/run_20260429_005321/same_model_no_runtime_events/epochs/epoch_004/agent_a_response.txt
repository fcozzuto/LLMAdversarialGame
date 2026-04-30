def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    # Pick a target resource with best advantage (opponent far / us close).
    best_rx = None
    best_ry = None
    best_adv_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer bigger (do-ds), then closer to it, then safer (farther from opponent).
        key = (do - ds, -ds, do, rx, ry)
        if best_adv_key is None or key > best_adv_key:
            best_adv_key = key
            best_rx, best_ry = rx, ry

    if best_rx is not None:
        tx, ty = best_rx, best_ry
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            ds = dist(nx, ny, tx, ty)
            do = dist(ox, oy, tx, ty)
            # Maximize our likelihood to beat opponent on the target.
            # Add small tie-breakers for staying far from opponent and progressing.
            val = (do - ds) * 1000 - ds * 3 - dist(nx, ny, ox, oy) * 1
            # If opponent is adjacent to the target, try to approach/contest by prioritizing ds.
            if resources and do == 1:
                val += -ds * 30
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources (or all blocked): move to maximize distance from opponent while keeping central-ish.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dopp = dist(nx, ny, ox, oy)
        dcent = dist(nx, ny, cx, cy)
        val = dopp * 10 - dcent * 1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]