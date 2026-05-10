def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # If we are on a resource, stay (collection handled by engine).
    for rx, ry in resources:
        if sx == rx and sy == ry:
            return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    # Pick a "contestable" resource: maximize (opp_dist - self_dist), tie-break by smaller self_dist.
    best_r = resources[0]
    best_gap = cheb(ox, oy, best_r[0], best_r[1]) - cheb(sx, sy, best_r[0], best_r[1])
    best_sd = cheb(sx, sy, best_r[0], best_r[1])
    for rx, ry in resources[1:]:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gap = od - sd
        if gap > best_gap or (gap == best_gap and (sd < best_sd or (sd == best_sd and (rx + ry) < (best_r[0] + best_r[1])))):
            best_gap = gap
            best_sd = sd
            best_r = [rx, ry]

    tr, ty = int(best_r[0]), int(best_r[1])

    # One-step evaluation toward target, also slightly discourage moves that let opponent get closer to target.
    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tr, ty)
        opd = cheb(ox, oy, tr, ty)  # opponent moves next turn; use current as stable anchor
        # Prefer faster approach; if we are already close, prefer blocking-like moves that increase opp reach relative to us.
        val = -myd * 10 + (opd - myd)
        # If this move lands on a resource, prioritize immediate collection.
        for rx, ry in resources:
            if nx == rx and ny == ry:
                val += 1000
                break
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move