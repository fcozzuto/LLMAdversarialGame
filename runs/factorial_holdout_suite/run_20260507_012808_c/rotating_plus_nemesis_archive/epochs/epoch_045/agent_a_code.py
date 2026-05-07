def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def greedy_step(x, y, tx, ty):
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            v = -cheb((nx, ny), (tx, ty))
            if v > bestv or (v == bestv and (nx, ny) < (x + best[0], y + best[1])):
                bestv = v
                best = (dx, dy)
        return best
    if not res:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -(abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # pick target that we can reach sooner than opponent, with slight bias to closer resources
        best_target_score = -10**18
        for tx, ty in res:
            my1 = cheb((nx, ny), (tx, ty))
            op1 = cheb((ox, oy), (tx, ty))
            # 2-step lookahead to handle local obstacle avoidance deterministically
            sx2d, sy2d = greedy_step(nx, ny, tx, ty)
            n2x, n2y = nx + sx2d, ny + sy2d
            my2 = cheb((n2x, n2y), (tx, ty))
            # prefer targets where we are closer than opponent; break ties by absolute proximity
            target_score = (op1 - my2) * 10 - my1 - (my2 == my1) * 0.1
            if target_score > best_target_score:
                best_target_score = target_score
        # also encourage moving away from opponent if no clear target
        escape = cheb((nx, ny), (ox, oy))
        v = best_target_score + 0.02 * escape
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]