def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step_toward(tx, ty):
        # Prefer moves that strictly reduce distance; deterministic tie-break by move order.
        move_order = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]
        best = None
        curd = cheb(sx, sy, tx, ty)
        for dx, dy in move_order:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            nd = cheb(nx, ny, tx, ty)
            # Aggressive: reduce distance first; if equal, move that improves our lead vs opponent.
            adv = (cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty))
            key = (nd - curd, nd, adv, nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        if best is None:
            return [0, 0]
        return best[1]

    # Strategic change: intercept likely sweep progress by maximizing (opp_dist - self_dist),
    # but if no winning resource exists, prioritize resources with minimal self_dist that are
    # on/near the opponent's current Chebyshev frontier relative to us.
    if not resources:
        # With no resources, head toward center to avoid getting trapped by sweep.
        target = (w // 2, h // 2)
        tx, ty = target
        return step_toward(tx, ty)

    best_tx, best_ty = resources[0]
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        advantage = do - ds  # positive means we can reach no later than opponent in Chebyshev steps
        # Frontier proxy: match opponent's relative progress in y (sweep rows -> y matters more).
        y_front = abs(ry - oy)
        # Prefer to take immediately winnable targets; otherwise pick the one we reduce distance to fastest,
        # while keeping it on opponent's sweep vicinity to deny later.
        key = (
            0 if advantage > 0 else 1,
            -advantage if advantage > 0 else 0,   # larger advantage first when winnable
            ds,                                   # then closer first
            y_front,                               # then on opponent's sweep frontier
            rx, ry                                 # deterministic
        )
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = rx, ry

    return step_toward(best_tx, best_ty)