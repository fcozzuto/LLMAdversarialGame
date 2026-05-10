def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break: fixed order.
    best = None
    best_score = None

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_dir_score(x, y):
        # Higher is better for evader, lower is better for pursuer
        # Choose farthest corner from opponent (evader) or nearest corner to opponent (pursuer).
        if is_evader:
            bestd = -1
            for cx, cy in corners:
                d = cheb(x, y, cx, cy) + 0.25 * cheb(ox, oy, cx, cy)
                if d > bestd:
                    bestd = d
            return bestd
        else:
            bestd = 10**9
            for cx, cy in corners:
                d = cheb(x, y, cx, cy) + 0.25 * cheb(ox, oy, cx, cy)
                if d < bestd:
                    bestd = d
            return bestd

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # Wall/obstacle sensitivity: discourage stepping adjacent to obstacles if it blocks later.
        adj_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx, ty = nx + adx, ny + ady
                if (tx, ty) in obstacles:
                    adj_obs += 1
        # Score design
        if is_evader:
            # Prefer larger distance; also bias toward corners.
            score = (-d, adj_obs, -corner_dir_score(nx, ny), dx, dy)
            # Minimization by constructing negatives
        else:
            score = (d, adj_obs, corner_dir_score(nx, ny), dx, dy)

        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]