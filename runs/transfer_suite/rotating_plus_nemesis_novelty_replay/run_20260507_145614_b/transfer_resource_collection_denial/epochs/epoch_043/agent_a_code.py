def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if resources:
        for r in resources:
            if (sx, sy) == (r[0], r[1]):
                return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not valid(nx, ny):
            continue

        score = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            if myd == 0:
                score += 1000000
            else:
                # Favor resources we can reach sooner than opponent; discourage those they can deny early.
                # Chebyshev distance is consistent with diagonal moves.
                score += (opd - myd) * 120 - myd * 3

            # Small repulsion from being too close to obstacles (reduces getting stuck/denied near clutter).
            # Count obstacles within 1-step Chebyshev radius.
            for oxp, oyp in obstacles:
                if cheb(nx, ny, oxp, oyp) <= 1:
                    score -= 8

        # Tie-break: slightly prefer moves that reduce distance to nearest resource.
        mn = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < mn:
                mn = d
        score -= mn

        if score > best_score:
            best_score = score
            best = (dxi, dyi)

    return [int(best[0]), int(best[1])]