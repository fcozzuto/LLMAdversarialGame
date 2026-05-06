def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        ax = ax - bx
        if ax < 0: ax = -ax
        ay = ay - by
        if ay < 0: ay = -ay
        return ax + ay

    def best_resource_from(nx, ny):
        best = None  # (key, rx, ry)
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer states where we beat opponent; penalize where opponent has large advantage.
            diff = od - sd
            # Also prefer closer resources overall.
            key = (-(diff), sd, (rx + ry) % 7, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        return best[1], best[2]

    # If resources exist, chase an advantaged target; otherwise stay near center-ish.
    if resources:
        # Compute a dynamic "row sweep defense": if opponent is sweeping rows, try to be on same row/near its path.
        # We approximate sweep by aiming for resources with smaller y (deterministically ties).
        target_rx, target_ry = best_resource_from(sx, sy)
    else:
        target_rx, target_ry = (w // 2), (h // 2)

    # Choose move maximizing: (advantage swing) + (approach target) - (being easily closer to opponent vs target).
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if resources:
            trx, try_ = best_resource_from(nx, ny)
            sd = man(nx, ny, trx, try_)
            od = man(ox, oy, trx, try_)
            diff = od - sd
            # Encourage grabbing along our side when opponent is far; discourage marching into its direct race.
            # Add mild bias to reduce distance to opponent to intercept (diagonal allowed).
            inter = -man(nx, ny, ox, oy)
            # Penalize moving away from chosen target from current state to avoid dithering.
            stab = man(nx, ny, target_rx, target_ry) - man(sx, sy, target_rx, target_ry)
            # Prefer moves that change parity less (deterministic tie-breaking via offsets).
            score_tuple = (
                -diff,              # smaller is better => we want larger diff
                sd,                 # closer is better
                stab,               # less increase is better
                -inter,             # more negative (closer to opponent) better
                (nx * 3 + ny * 5) % 11,
                nx, ny
            )
        else:
            # No resources: just move toward the center.
            sd = man(nx, ny, target_rx, target_ry)
            score_tuple = (sd, (nx * 3 + ny * 5) % 11, nx, ny)

        if best_score is None or score_tuple < best_score:
            best_score = score_tuple
            best_move = [dx, dy]

    return best_move