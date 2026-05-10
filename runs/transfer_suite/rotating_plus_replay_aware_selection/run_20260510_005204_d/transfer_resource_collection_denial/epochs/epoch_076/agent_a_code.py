def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Target: maximize (opponent advantage vs ours), tie-break to earlier coords
    best_tx, best_ty = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - myd, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_tx, best_ty = rx, ry

    # One-step evaluation toward target, with strong contest pressure
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        myd2 = cheb(nx, ny, best_tx, best_ty)
        opd2 = cheb(ox, oy, best_tx, best_ty)

        # Prefer moves that reduce our distance and increase opponent distance relative.
        # Big bonus if we could reach the resource strictly before opponent (tie-break favors points).
        score = 0
        score += (best_score is None) * 0  # no-op for determinism
        score += (opd2 - myd2) * 20
        score += (20 - myd2)  # closer is better
        score -= (cheb(nx, ny, ox, oy) == 0) * 5  # avoid landing on opponent if possible

        # If move lands on another resource, ensure it's selected
        if (nx, ny) in set(tuple(r) for r in resources):
            score += 500 - myd2 * 2

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]