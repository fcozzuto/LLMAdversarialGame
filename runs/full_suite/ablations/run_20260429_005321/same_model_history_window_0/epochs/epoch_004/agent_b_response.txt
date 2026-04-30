def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"] if observation.get("remaining_resource_count", 0) else []
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Deterministic fallback: move toward center, avoiding obstacles
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -((nx - cx) ** 2 + (ny - cy) ** 2)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Choose a target resource that we are relatively more likely to secure.
    best_t = None
    best_key = 10**9
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Key: prefer resources with smaller "our lead" deficit (we want md < od).
        key = md - 0.85 * od
        # Tie-break: closer absolute distance.
        key = key * 10 + md
        if key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    # Evaluate candidate moves with target progress and opponent pressure.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Progress toward target (dominant), plus mild center preference and opponent-avoidance.
        v = (-myd) * 1000 + (opd) * 5 - ((nx - cx) ** 2 + (ny - cy) ** 2) * 0.2
        # Small anti-stall: discourage staying if a better progress exists.
        v += -1 if (dx == 0 and dy == 0) else 0
        # If opponent is very close, bias toward reducing their distance to the same target.
        if cheb(ox, oy, tx, ty) <= 1:
            v += -cheb(nx, ny, ox, oy)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]