def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if remaining <= 0 or not resources:
        tx, ty = ox, oy
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Choose best target resource deterministically with opponent-aware priority
    best_res = None; best_rv = -10**18
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; tie-break by resource coordinates
        rv = (d_opp - d_self) - 0.05 * cheb(sx, sy, ox, oy) + (-0.01) * (rx * 100 + ry)
        if rv > best_rv:
            best_rv = rv; best_res = (rx, ry)

    tx, ty = best_res
    best = None; bestv = -10**18
    for dx, dy, nx, ny in legal:
        v = 0
        v += -cheb(nx, ny, tx, ty)  # move closer to target
        v += 0.02 * (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))  # slight favor away from opponent
        # avoid stepping into squares that are closer to opponent than we are (reduces being contested)
        if cheb(nx, ny, ox, oy) <= cheb(nx, ny, tx, ty):
            v -= 0.1
        # deterministic tie-breaker
        v += -1e-6 * (dx + 2 * dy + 0.001 * nx + 0.0001 * ny)
        if v > bestv:
            bestv = v; best = (dx, dy)

    return [best[0], best[1]]