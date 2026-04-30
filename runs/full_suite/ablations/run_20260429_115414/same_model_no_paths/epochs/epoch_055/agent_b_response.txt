def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_val = -10**9

    # Precompute advantage target score at current position
    # Advantage: opponent farther than us -> prefer
    res_list = resources if resources else [(w - 1, h - 1), (0, h - 1), (w - 1, 0), (0, 0)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        on_resource = (nx, ny) in resources

        # Local safety penalty: discourage being adjacent to obstacles
        adj_obs = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (nx + ex, ny + ey) in obstacles:
                    adj_obs += 1

        # Choose best resource target from this hypothetical state
        # Score favors reaching a resource sooner than opponent.
        if resources:
            best_target = -10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Higher is better: we want ds small and (do-ds) large
                tgt = (do - ds) * 3 - ds
                if (rx, ry) == (nx, ny):
                    tgt += 30
                if tgt > best_target:
                    best_target = tgt
            val = best_target
        else:
            # No visible resources: go toward far corner deterministically
            tx, ty = (w - 1, h - 1) if sx < w // 2 else (0, h - 1 if sy < h // 2 else 0)
            val = -cheb(nx, ny, tx, ty)

        val += (3 if on_resource else 0) - adj_obs * 0.35

        # Tiny deterministic tie-breaker toward decreasing distance to opponent to potentially contest
        val += -cheb(nx, ny, ox, oy) * 0.05

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]