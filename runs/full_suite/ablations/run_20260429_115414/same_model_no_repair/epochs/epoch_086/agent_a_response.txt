def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = {(p[0], p[1]) for p in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Prefer targeting resources closer to us AND significantly farther from opponent.
    # Deterministic mode switch to change behavior if we got stuck previously.
    mode = 1 if (observation.get("turn_index", 0) % 2 == 0) else 0

    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Evaluate best target resource for this move.
        # Score: want large advantage (opponent farther than us), plus small tie-break to reduce our distance.
        move_best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # higher is better
            # Mode changes emphasis:
            # mode=0: push advantage more; mode=1: push reaching faster.
            val = adv * (3 if mode == 0 else 1) - (myd * (1 if mode == 0 else 2))
            if move_best is None or val > move_best:
                move_best = val
        if move_best is None:
            continue

        # If equal, deterministically prefer moves that bring us closer to the most "promising" resource.
        if best_val is None or move_best > best_val:
            best_val = move_best
            best = (dx, dy)
        elif move_best == best_val:
            # tie-break using lexicographic on distance to nearest resource
            # (lower is better)
            my_near = min(cheb(nx, ny, rx, ry) for rx, ry in resources if (rx, ry) not in obs)
            bx, by = best
            ox_near = min(cheb(sx + bx, sy + by, rx, ry) for rx, ry in resources if (rx, ry) not in obs)
            if my_near < ox_near:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]