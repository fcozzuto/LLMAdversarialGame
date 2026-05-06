def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    viable = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            viable.append((dx, dy))
    if not viable:
        return [0, 0]

    # Advantage-oriented: after our move, choose the resource that maximizes (opp_dist - self_dist),
    # i.e., we are closer than the opponent; tie-break by our absolute proximity.
    def best_after(nx, ny):
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            # Secondary: prefer smaller sd and smaller (rx+ry) for determinism
            key = (adv, -sd, -(rx + ry))
            if best is None or key > best[0]:
                best = (key, adv, sd)
        return best[0] if best is not None else (-10**9, 0, 0)

    # Small "denial" bias: also consider how close we keep to opponent's nearest resource.
    def opponent_pressure(nx, ny):
        opp_best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            od = cheb(ox, oy, rx, ry)
            key = (-(od), (rx + ry))
            if opp_best is None or key > opp_best[0]:
                opp_best = (key, od, rx, ry)
        if opp_best is None:
            return 0
        _, od, rx, ry = opp_best[0], opp_best[1], opp_best[2], opp_best[3]
        # Prefer states that reduce our distance to opponent's best target (faster convergence to contest).
        return -cheb(nx, ny, rx, ry)

    best_move = (0, 0)
    best_key = None
    for dx, dy in viable:
        nx, ny = sx + dx, sy + dy
        k1 = best_after(nx, ny)
        k2 = opponent_pressure(nx, ny)
        # Combine keys deterministically
        combined = (k1[0], k1[1], k1[2], k2, -cheb(nx, ny, w - 1, h - 1), -cheb(nx, ny, 0, 0))
        if best_key is None or combined > best_key:
            best_key = combined
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]