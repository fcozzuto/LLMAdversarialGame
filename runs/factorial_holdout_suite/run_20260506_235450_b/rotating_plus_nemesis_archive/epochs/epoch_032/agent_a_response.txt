def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = r[0], r[1]
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))

    # Prefer moves that create immediate competitive advantage on the best resource.
    # Avoid resources where the opponent is strictly closer (unless we can catch up quickly).
    turns = observation.get("turns_remaining", 999)
    best = (None, None)  # (gain, -self_dist_after)
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        local_best_gain = -10**9
        local_best_self = 10**9
        for (tx, ty) in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # If opponent closer, only consider if we can reach no later than them soon enough.
            if do < ds and ds > 1:
                if ds > max(1, turns // 3):
                    continue
            gain = (do - ds)  # bigger is better: we are closer than opponent
            # Tie-breaker: smaller self distance
            if gain > local_best_gain or (gain == local_best_gain and ds < local_best_self):
                local_best_gain, local_best_self = gain, ds
        key = (local_best_gain, -local_best_self)
        if best[0] is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]