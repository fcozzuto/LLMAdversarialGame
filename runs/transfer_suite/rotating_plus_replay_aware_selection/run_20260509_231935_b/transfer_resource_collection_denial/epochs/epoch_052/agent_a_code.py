def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    if not res:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        if (nx, ny) in obs:
            return None
        return nx, ny

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    # Choose move to approach a "contested" resource where we are relatively closer than the opponent.
    # Also slightly reward moves that increase count of resources in immediate neighborhood.
    best_move = (0, 0)
    best_score = -10**18

    # Precompute a deterministic "priority" score for each resource from current positions.
    alpha = 1.1
    scored_resources = []
    for r in res:
        if r in obs:
            continue
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        # Higher means better: smaller ds, larger (do - ds) => we are winning contest.
        contest = (do - ds)
        scored_resources.append((r, -ds + alpha * contest))

    if not scored_resources:
        return [0, 0]
    scored_resources.sort(key=lambda t: (-t[1], t[0][0], t[0][1]))

    # Evaluate candidate moves with a small lookahead: choose the best target resource for the resulting position.
    for dx, dy in dirs:
        nxt = clamp_move(dx, dy)
        if nxt is None:
            continue
        nx, ny = nxt
        # quick neighborhood count to avoid dithering
        neigh = 0
        for rx, ry in res:
            if abs(rx - nx) <= 1 and abs(ry - ny) <= 1:
                if (rx, ry) not in obs:
                    neigh += 1

        # Pick the best target among top-k currently promising resources (k small for speed/determinism)
        score = -10**18
        k = 6 if len(scored_resources) > 6 else len(scored_resources)
        for i in range(k):
            r, base = scored_resources[i]
            dsn = dist((nx, ny), r)
            don = dist((ox, oy), r)
            val = -dsn + alpha * (don - dsn)
            # capture incentive
            if dsn == 0:
                val += 50
            score = val if val > score else score

        # tie-breakers: deterministic preference to progress right then up, but only if near-equal
        score = score + 0.03 * neigh + 1e-6 * (dx * 3 - dy * 2)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) > best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]