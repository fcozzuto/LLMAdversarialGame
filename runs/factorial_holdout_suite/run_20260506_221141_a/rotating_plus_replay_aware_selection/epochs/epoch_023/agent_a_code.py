def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh
    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # If no resources, move to safer central-ish cell while avoiding obstacles.
    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            # Prefer moves that don't get immediately stuck (more legal neighbors).
            neigh = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if legal(tx, ty):
                    neigh += 1
            v = -d + 0.3 * neigh + (0.01 if (dx, dy) != (0, 0) else 0.0)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # One-step lookahead: pick move that maximizes chance to win nearest resource race.
    best = [0, 0]
    bestv = -10**18
    # Tie-break: slight preference for increasing our distance to opponent to reduce sweeps.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # For each resource, compute "race" advantage from next state.
        v = 0.0
        best_res = None
        best_adv = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # ds < do => likely win; ds==do => contested; ds>do => likely lose.
            adv = (do - ds)  # positive is good
            # Also bias toward closer resources once race tie is similar.
            cand = (adv, -ds)
            if best_adv is None or cand > best_adv:
                best_adv = cand
                best_res = (rx, ry, ds, do, adv)
        rx, ry, ds, do, adv = best_res
        # Main objective: maximize race advantage, then minimize our distance to get first.
        # Add tiny obstacle-escape term to avoid oscillation near blocked areas.
        neigh = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if legal(tx, ty):
                neigh += 1
        v = 10.0 * adv - 0.8 * ds + 0.05 * (cheb(nx, ny, ox, oy)) + 0.15 * neigh
        if (dx, dy) != (0, 0):
            v += 0.02  # break symmetry deterministically in favor of moving
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best