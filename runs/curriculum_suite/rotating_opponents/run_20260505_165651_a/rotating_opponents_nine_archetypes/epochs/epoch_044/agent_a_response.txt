def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]
    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dme = king_dist(nx, ny, ox, oy)
            v = dme  # run away deterministically if no resources
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose based on net advantage over opponent on best few resources, plus anti-probe spacing.
    top_resources = sorted(resources, key=lambda r: king_dist(sx, sy, r[0], r[1]))[:3]
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_opp_space = king_dist(nx, ny, ox, oy)
        v = 0.0
        # Encourage being closer than opponent to resources; strongly discourage being worse.
        for rx, ry in top_resources:
            dm = king_dist(nx, ny, rx, ry)
            do = king_dist(ox, oy, rx, ry)
            margin = do - dm  # positive means we are closer
            v += 2.2 * margin - 0.15 * dm
        # If opponent is extremely near, prioritize separation and not just resource chasing.
        if king_dist(sx, sy, ox, oy) <= 2:
            v += 0.9 * my_opp_space
        # Tie-break: avoid head-on moves that reduce distance to opponent too much.
        v -= 0.05 * king_dist(nx, ny, ox, oy)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]