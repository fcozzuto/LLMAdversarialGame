def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    # If standing on a resource, stay (ties broken deterministically by turn parity)
    if (sx, sy) in set(resources):
        return [0, 0] if (int(observation.get("turn_index", 0)) % 2 == 0) else [0, 0]

    turn = int(observation.get("turn_index", 0))

    best = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Score move by best resource we can secure relative to opponent
        move_best = -10**9
        found = False
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Prefer closer resources and those we can reach no slower than opponent
            # Cheb distance is in [0..7]; use strong incentives for advantage.
            advantage = opd - myd
            if advantage >= 0:
                val = 100 - myd - (0 if advantage == 0 else (opd - myd) * 5)
            else:
                # If we can't beat them, still move toward the least-losing target.
                val = 30 - (myd + (-advantage) * 2)

            # Tie-break deterministically toward lower (rx,ry) but depend on move
            val -= ((rx * 31 + ry * 17 + dx * 7 + dy * 13 + turn) % 7) * 0.01
            if val > move_best:
                move_best = val
                found = True

        # Small preference for moving that reduces distance to opponent's position (disruption)
        disrupt = -0.1 * cheb(nx, ny, ox, oy)
        total = move_best + disrupt

        if (not found) or (best_score is None) or (total > best_score) or (total == best_score and (dx, dy) < best):
            best_score = total
            best = (dx, dy)

    return [int(best[0]), int(best[1])]