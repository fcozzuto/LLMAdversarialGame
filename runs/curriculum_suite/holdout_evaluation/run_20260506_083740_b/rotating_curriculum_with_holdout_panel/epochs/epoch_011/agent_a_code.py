def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = list(observation.get("resources", []) or [])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]
    if not resources:
        # drift toward center to avoid stagnation
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in cand:
            d = (abs(nx - tx) + abs(ny - ty))
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Select move that maximizes "resource steal advantage" over opponent.
    # Advantage = (opponent distance) - (our distance), prefer strong margins; avoid giving opponent quick access.
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in cand:
        best_res_key = None
        # Evaluate the best target resource for this move
        for rx, ry in resources:
            myd = abs(nx - rx) + abs(ny - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            # Higher is better: opponent farther than us.
            adv = opd - myd
            # Penalize if opponent is closer or equal and we are not significantly closer.
            # Small bias to prefer nearer resources to convert advantage into pickup.
            k = (adv, -myd, -abs(nx - rx) - abs(ny - ry), -opd)
            if best_res_key is None or k > best_res_key:
                best_res_key = k
        # Additional tie-break: prefer reducing our distance to the closest remaining resource.
        close_my = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        close_opp = min(abs(ox - rx) + abs(oy - ry) for rx, ry in resources)
        # Prefer not stepping into opponent-favored vicinity.
        safety = (close_opp - close_my)
        key = (best_res_key[0], best_res_key[1], safety, -close_my, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]