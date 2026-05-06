def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    # Target score: negative is good (we aim to be closer than opponent for contested resources).
    # Also add a small preference for going towards a resource even if we can't beat opponent yet.
    best = (0, 0)
    best_val = None

    # If no resources, drift toward center.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bestd = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = king(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Precompute which resources are currently contested (opponent at least as close).
    contested = []
    for rx, ry in resources:
        ds = king(sx, sy, rx, ry)
        do = king(ox, oy, rx, ry)
        if do <= ds:
            contested.append((rx, ry, ds, do))
    if not contested:
        # If nothing is contested, head to the closest resource to us, but still consider opponent pressure.
        contested = [(rx, ry, king(sx, sy, rx, ry), king(ox, oy, rx, ry)) for (rx, ry) in resources]

    # For efficiency, evaluate only a few best candidates.
    contested.sort(key=lambda t: (t[3] - t[2], t[3], t[2]))  # prefer resources where opp is not far ahead; then closer
    candidates = contested[:6]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = 0.0
        # Primary: minimize (our_d - opp_d) over contested candidates.
        # Secondary: reduce our distance to the most relevant resource.
        for rx, ry, ds, do in candidates:
            dsn = king(nx, ny, rx, ry)
            don = do  # opponent doesn't move this turn; keep fixed for stability
            diff = dsn - don  # negative good
            if do <= ds:
                # Contest: focus strongly on beating/keeping parity.
                val += diff * 3.0
                val += dsn * 0.1
            else:
                # Non-contested: still guide towards it.
                val += diff * 0.6
                val += dsn * 0.05
        # Slight tie-break: avoid moving away from opponent too much when we must intercept.
        val += abs(nx - ox) + abs(ny - oy) * 0.001

        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]