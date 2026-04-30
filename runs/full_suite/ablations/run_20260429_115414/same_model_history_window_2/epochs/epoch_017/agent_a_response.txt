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

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources or remaining <= 0:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, tx, ty) - 0.2 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [int(best[0]), int(best[1])]

    def neigh_free(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                cnt += 1
        return cnt

    best = None; bestv = -10**18
    eps = 1e-9
    for dx, dy, nx, ny in legal:
        v = 0.0
        # Prefer immediate capture
        min_my = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            if d1 < min_my: min_my = d1
            if d2 < min_opp: min_opp = d2
        v += -min_my
        # Target resources where we are relatively closer than opponent
        # (computed without full search: aggregate over resources using a deterministic transform)
        rel = 0.0
        for rx, ry in resources:
            dmy = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # higher when we are closer; heavily favor winning the race
            rel += (dop - dmy) / (1 + dmy + dop)
        v += 0.6 * rel
        # Avoid getting trapped: higher neighborhood mobility is better
        v += 0.08 * neigh_free(nx, ny)
        # Mildly keep distance from opponent to reduce collisions/pressure
        v += 0.02 * cheb(nx, ny, ox, oy)
        # Deterministic tie-break: lexicographic on move
        if v > bestv + eps or (abs(v - bestv) <= eps and (dx, dy) < (best[0], best[1])):
            bestv = v; best = (dx, dy)

    return [int(best[0]), int(best[1])]