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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_target(tx, ty):
        if tx < 0: tx = 0
        if ty < 0: ty = 0
        if tx >= gw: tx = gw - 1
        if ty >= gh: ty = gh - 1
        return tx, ty

    def best_resource():
        best = None
        bestv = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier, then closer, then stable tie-break
            v = (d_op - d_me) * 1000 - d_me * 3 + (rx + ry) * 0.0001
            # If opponent is already extremely close, penalize less (we'll still try to contest if v is best)
            if d_op <= 1 and d_me > d_op:
                v -= 200
            if v > bestv:
                bestv = v
                best = (rx, ry)
        return best

    if resources:
        target = best_resource()
    else:
        target = (3 if sx > (gw - 1) // 2 else (4 if sx < (gw - 1) // 2 else sx),
                  3 if sy > (gh - 1) // 2 else (4 if sy < (gh - 1) // 2 else sy))

    tx, ty = clamp_target(target[0], target[1])

    best_move = [0, 0]
    best_score = -10**18
    # Evaluate each legal move: maximize advantage (opponent distance - our distance) to the chosen target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # If we can step onto target, strongly prefer
        if d_me == 0:
            score = 10**12
        else:
            score = (d_op - d_me) * 1000 - d_me * 5
        # Slightly discourage moving away from center if target is missing/weak
        if not resources:
            cx, cy = (gw - 1) // 2, (gh - 1) // 2
            score -= cheb(nx, ny, cx, cy) * 2
        # Deterministic tie-break
        score += (dx + 1) * 0.01 + (dy + 1) * 0.001
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move