def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx if dx >= dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        best = (0, 0); bestk = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            # reduce opponent options: prefer moves that maximize distance from them while still edging toward board center
            k = (cheb(nx, ny, ox, oy), -cheb(nx, ny, w // 2, h // 2), nx, ny)
            if bestk is None or k > bestk: bestk = k; best = (dx, dy)
        return [best[0], best[1]]

    # One-step lookahead: choose move that creates the largest "tempo" lead to some resource.
    best = (0, 0); bestScore = -10**18
    # Precompute a stable ordering of resources (for deterministic tie-breaking)
    res_sorted = sorted(resources, key=lambda p: (p[0], p[1]))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Obstacle-aware: avoid moving next to obstacles too much (to reduce getting trapped)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    adj_obs += 1

        # Tempo/contested resource score
        localBest = -10**18
        for rx, ry in res_sorted:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Lead if we can reach strictly sooner; small tie-break to prefer picking earlier.
            lead = do - ds
            # Also lightly prefer resources closer to the opponent's current direction to deny them (without tracking paths).
            deny = -abs(rx - (ox + (1 if ox < w - 1 else -1))) - abs(ry - (oy + (1 if oy < h - 1 else -1)))
            score = (lead * 100) - ds + deny - 0.5 * adj_obs + 0.000001 * (-rx) + 0.0000001 * (-ry)
            if score > localBest:
                localBest = score

        # If we're not making progress to any resource, bias slightly toward opponent-distance reduction (edge contest).
        fallback = -cheb(nx, ny, ox, oy) * 0.01 - cheb(nx, ny, w // 2, h // 2) * 0.001
        total = localBest + fallback
        if total > bestScore:
            bestScore = total
            best = (dx, dy)

    return [best[0], best[1]]