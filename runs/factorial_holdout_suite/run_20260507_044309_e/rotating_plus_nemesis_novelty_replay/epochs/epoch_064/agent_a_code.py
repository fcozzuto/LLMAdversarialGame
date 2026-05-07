def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # Heuristic: prioritize moves that (1) reduce our best distance to resources, (2) maximize "winning" of contested resources,
    # and (3) when tied, move closer (cheb) to the most valuable contested resource.
    best_move = None
    best_key = None
    # deterministic resource ordering for tie-breaks
    res_sorted = sorted((tuple(r) for r in res), key=lambda p: (p[0], p[1]))
    for dx, dy, nx, ny in valid:
        # compute best contested advantage if we reach a resource first (approx: current distances)
        best_adv = -10**9
        best_ds = 10**9
        best_r = res_sorted[0]
        # also track our min distance after move
        min_ds = 10**9
        for rx, ry in res_sorted:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < min_ds:
                min_ds = ds
            adv = do - ds
            if adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and (rx, ry) < best_r))):
                best_adv, best_ds, best_r = adv, ds, (rx, ry)

        # Opponent pressure: how close opponent is to our best target
        opp_on_best = cheb(ox, oy, best_r[0], best_r[1])

        # Score key: maximize winning advantage, minimize our distance, and keep deterministic movement preference
        key = (best_adv, -min_ds, -opp_on_best, -dx, -dy, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]