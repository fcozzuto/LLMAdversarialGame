def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Build preference list of resources: those we can reach earlier than opponent.
    # If none, pick the resource with smallest time gap (still toward center-ish).
    scored_resources = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gap = ds - do
        center = abs(rx - (W - 1) / 2.0) + abs(ry - (H - 1) / 2.0)
        scored_resources.append((gap, ds, center, rx, ry))
    scored_resources.sort()
    candidates = []
    for r in scored_resources[:6]:
        gap, ds, center, rx, ry = r
        if gap <= 0:
            candidates.append((0.0, gap, ds, rx, ry))
    if not candidates:
        # Fall back to time advantage even if slightly negative/positive; deterministic order.
        for r in scored_resources[:6]:
            gap, ds, center, rx, ry = r
            candidates.append((gap, gap, ds, rx, ry))

    best = None
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        # Avoid walking adjacent to opponent unless it helps secure an earlier resource.
        dist_o = cheb(nx, ny, ox, oy)
        block_pen = -2.5 if dist_o <= 1 else 0.0

        # Prefer moves that improve our best candidate capture prospects.
        move_val = block_pen
        for _, gap, ds, rx, ry in candidates:
            dnew = cheb(nx, ny, rx, ry)
            # If we are ahead (or can become ahead), strongly prefer; otherwise penalize.
            advantage = (ds - (cheb(ox, oy, rx, ry)))
            # Use post-move gap: (our time to target - opponent time)
            post_gap = dnew - cheb(ox, oy, rx, ry)
            # Lower post_gap is better; reaching resource gets big bump.
            reach_bonus = 8.0 if (nx == rx and ny == ry) else 0.0
            val = reach_bonus + (3.0 if post_gap <= 0 else -1.5) + (-2.0 * post_gap) + (0.15 * advantage)
            move_val += val

        # Small tie-breaker: drift toward middle to reduce being trapped early.
        move_val += -0.02 * (abs(nx - (W - 1) / 2.0) + abs(ny - (H - 1) / 2.0))

        if best is None or move_val > best_val:
            best_val = move_val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]