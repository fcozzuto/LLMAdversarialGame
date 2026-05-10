def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Greedy late: favor immediate collection
    late = 1 if turns_remaining <= 8 else 0

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    res_set = set(tuple(r) for r in resources)

    def best_adv_at(cx, cy):
        best = -10**9
        bestd = 10**9
        # Consider each resource; advantage = how much closer we are than opponent
        for rx, ry in resources:
            d_me = cheb(cx, cy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_me
            if d_me < bestd:
                bestd = d_me
            if adv > best:
                best = adv
            elif adv == best and d_me < bestd:
                bestd = d_me
        return best, bestd

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        if (nx, ny) in res_set:
            score = 10**12 + (1 if late else 0) * 10**6
        else:
            adv, mind = best_adv_at(nx, ny)
            # Prefer higher advantage, then closer best target, then slight center bias for determinism
            center_bias = -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)
            score = adv * 10**6 - mind * 10 - center_bias
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]