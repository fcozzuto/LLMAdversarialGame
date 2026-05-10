def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    # Evaluate move by choosing a target resource and estimating who arrives first
    # Score favors: our arrival earlier; then being closer; then hurting opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_best = None
        for rx, ry in resources:
            rxd, ryd = int(rx), int(ry)
            my_d = cheb(nx, ny, rxd, ryd)
            op_d = cheb(ox, oy, rxd, ryd)
            # If we reach sooner than opponent, big positive; if later, negative.
            advantage = op_d - my_d
            score = (advantage * 1000) - my_d * 10 + op_d
            # Deterministic tie-break by coordinate ordering
            score = (score, -rxd, -ryd)
            if my_best is None or score > my_best:
                my_best = score
        if my_best is None:
            continue
        if best is None or my_best > best:
            best = my_best
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]