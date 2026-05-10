def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    # Pick best resource by who can reach first (chebyshev distance), tie-break toward our closer / deterministic.
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # primary: maximize (opd - myd); secondary: minimize myd; tertiary: deterministic by coords
        key = (opd - myd, -myd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    tx, ty = best[1], best[2]

    # Choose move that is safe and maximizes our advantage after the move.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        # If we step closer to the chosen target and keep opponent from being better, prefer it.
        opd2 = cheb(ox, oy, tx, ty)
        # Small bias toward moving in direction that reduces distance to target.
        key = (opd2 - myd2, -myd2, -dx, -dy)
        if best_move is None or key > best_move[0]:
            best_move = (key, dx, dy)

    # Fallback: if all moves blocked, stay.
    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]