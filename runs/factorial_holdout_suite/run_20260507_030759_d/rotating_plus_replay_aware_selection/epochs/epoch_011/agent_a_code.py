def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Prefer immediate collection, then maximize distance advantage over opponent to the best remaining resource.
    # If multiple moves tie, use a deterministic tie-breaker toward increasing x then y.
    best_move = (0, 0)
    best_score = None

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue

        move_score = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If we land on a resource, prioritize collecting it.
            collect_bonus = 500 if (nx == rx and ny == ry) else 0
            # Larger when we are closer than opponent.
            adv = od - sd
            # Small secondary preference: reduce own distance if we're not winning that resource.
            local = collect_bonus + adv * 40 - sd
            if local > move_score:
                move_score = local

        # Deterministic tie-break: prefer smaller |dx| then smaller |dy| then lexicographic by (mx, my)
        tie_key = (move_score, -abs(mx), -abs(my), mx, my)
        if best_score is None or tie_key > best_score:
            best_score = tie_key
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]