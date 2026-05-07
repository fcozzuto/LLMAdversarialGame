def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def center_target():
        return (w - 1) // 2, (h - 1) // 2

    if not resources:
        tx, ty = center_target()
        best = [0, 0]
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
                    best = [dx, dy]
        return best

    res = [tuple(r) for r in resources]
    best_move = [0, 0]
    best_key = None

    # Deterministic: choose move that maximizes (opponent_distance - our_distance) for our best attainable resource
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        local_best_adv = -10**18
        local_best_our = 10**18
        local_best_r = None
        for rx, ry in res:
            our = cheb(nx, ny, rx, ry)
            opp = cheb(ox, oy, rx, ry)
            adv = opp - our
            # Prefer higher advantage; break ties with smaller our distance; then by coordinates for determinism
            if adv > local_best_adv or (adv == local_best_adv and (our < local_best_our or (our == local_best_our and (rx, ry) < local_best_r))):
                local_best_adv = adv
                local_best_our = our
                local_best_r = (rx, ry)
        # Global tie-break: higher advantage, then smaller our distance, then lexicographically smaller move
        key = (local_best_adv, -local_best_our, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move