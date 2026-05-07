def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best, bestv = [0, 0], -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            # prefer progress (lower d) and avoid moving into obstacles (already checked)
            v = -d
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Score each move by best target we can secure earlier than opponent; otherwise chase closest.
    best_move, best_val = [0, 0], -10**18
    eps = 0.0001
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # If multiple resources are visible, pick the most "winning" one from our perspective.
        move_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Positive when we can arrive sooner; big bonus for immediate pickup.
            # Slight preference for lower own distance to break ties deterministically.
            v = (do - ds) * 10.0 + (1.0 if ds == 0 else 0.0) - ds * eps
            if v > move_best:
                move_best = v
        # If we can't arrive sooner to any resource, still take the move that minimizes our distance to the closest resource.
        # (This fallback is naturally handled since v decreases with ds; but we add a safeguard.)
        if move_best < -1e9:
            move_best = -10**9
        if move_best > best_val:
            best_val = move_best
            best_move = [dx, dy]
    return best_move