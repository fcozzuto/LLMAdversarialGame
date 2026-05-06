def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        # Drift toward the half that is farther from the opponent corner.
        # Opponent usually sweeps; keep pressure by moving to the opposite central area.
        tx = (w - 1) // 4 if ox > (w - 1) // 2 else (3 * (w - 1)) // 4
        ty = (h - 1) // 4 if oy > (h - 1) // 2 else (3 * (h - 1)) // 4
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            key = (d, dx, dy)
            if best is None or key < best:
                best = key
        return [best[1], best[2]]

    # Choose the move that makes us best at the most "contested" resource:
    # favor targets that are close to us and far from the opponent.
    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_target_val = None
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Higher is better: small d_self, large d_opp. Add slight preference for immediate proximity.
            val = (d_opp - 1.3 * d_self) - 0.05 * (abs(rx - nx) + abs(ry - ny))
            if best_target_val is None or val > best_target_val:
                best_target_val = val
        # Also break ties deterministically toward larger forward progress to the best contested target.
        val2 = (best_target_val, -cheb(nx, ny, (w - 1) // 2, (h - 1) // 2), dx, dy)
        if best_val is None or val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]