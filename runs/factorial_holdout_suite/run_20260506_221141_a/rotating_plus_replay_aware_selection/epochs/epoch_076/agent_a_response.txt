def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best, bestv = [0, 0], -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move, best_val = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Choose the best resource to pursue from this hypothetical next position.
        # Prefer resources where we arrive earlier than opponent, and secondarily closer overall.
        cur_best = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Higher is better: win on timing (op_d - my_d), then prefer smaller my_d.
            v = (op_d - my_d) * 2 - my_d
            if v > cur_best:
                cur_best = v
        # Slight tie-break to keep motion consistent toward the most likely good region.
        if cur_best > best_val:
            best_val = cur_best
            best_move = [dx, dy]

    return best_move