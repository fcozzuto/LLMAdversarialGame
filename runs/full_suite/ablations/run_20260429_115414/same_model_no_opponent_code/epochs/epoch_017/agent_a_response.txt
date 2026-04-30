def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    rem = int(observation.get("remaining_resource_count", 0))

    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    rs = []
    for x, y in resources:
        x, y = int(x), int(y)
        if free(x, y):
            rs.append((x, y))
    if not rs:
        return [0, 0]

    even_policy = ((int(observation.get("turn_index", 0)) % 2) == 0)
    best = None
    for x, y in rs:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        if even_policy:
            # Contest resources where we are relatively closer; prefer also reasonably close overall.
            score = (od - sd) * 1000 - sd
        else:
            # Intercept: prioritize what opponent is closest to, but only if we can get there too.
            score = -(od * 1000) + (sd if sd <= od else -sd) - (sd > od) * 500
        # Tie-break: deterministic by coordinates
        score -= x + y * 0.01
        if best is None or score > best[0]:
            best = (score, (x, y))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Prefer getting closer to target; then prefer staying away from opponent.
        # When resources are scarce, prioritize survival less (more aggressive).
        aggression = 1 if rem <= 4 else 2
        score = -d_to_t * 10 + d_to_o * (1 if aggression == 1 else 2)
        # Small bias to continue in roughly the best direction
        score -= (abs((nx - sx) - (tx - sx)) > 8) * 0.1
        if bestm is None or score > bestm[0]:
            bestm = (score, (dx, dy))

    if bestm is None:
        return [0, 0]
    return [int(bestm[1][0]), int(bestm[1][1])]