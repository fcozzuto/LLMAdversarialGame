def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    late = 1 if turns_remaining <= 8 else 0

    best_move = [0, 0]
    best_score = -10**18

    res_set = set(tuple(r) for r in resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        score = 0

        if (nx, ny) in res_set:
            score += 10**6 + (5000 if late else 0)

        # Choose move that maximizes "interception advantage":
        # Prefer being strictly closer to some resource than opponent, especially early.
        best_adv = -10**9
        best_my = 10**9
        best_op = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = (opd - myd)  # positive means I can reach earlier
            if adv > best_adv:
                best_adv = adv
                best_my = myd
                best_op = opd
            elif adv == best_adv:
                if myd < best_my:
                    best_my = myd
                    best_op = opd

        # Tie-break shaping
        score += best_adv * (1000 if not late else 2000)
        score += (best_op - best_my) * 30
        score += -best_my if late else -best_my * 2

        # Mild repulsion from being too close to opponent (avoid giving them easy picks)
        dist_to_opp = cheb(nx, ny, ox, oy)
        score += (dist_to_opp - 1) * (5 if not late else 2)

        if score > best_score:
            best_score = score
            best_move = [nx - sx, ny - sy]

    return best_move