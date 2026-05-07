def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        d = abs(x1 - x2) + abs(y1 - y2)
        return d

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # One-step lookahead: pick move that maximizes advantage to an obtainable resource,
    # with a small "repel from opponent" term to disrupt nearest-resource behavior.
    resources_sorted = sorted((int(x), int(y)) for x, y in resources)

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate best target from this candidate position
        local_best = None
        for tx, ty in resources_sorted:
            myd = man(nx, ny, tx, ty)
            opd = man(ox, oy, tx, ty)

            # Disruptive behavior: prefer targets where we are significantly closer,
            # otherwise favor far-away-from-opp targets to prevent their grab.
            # Also lightly penalize moving into tight regions near obstacles.
            opp_prox = man(tx, ty, ox, oy)
            obs_pen = 0
            for ax, ay in ((tx + 1, ty), (tx - 1, ty), (tx, ty + 1), (tx, ty - 1)):
                if (ax, ay) in obstacles:
                    obs_pen += 1

            # Key components: maximize (opponent distance - my distance),
            # then minimize my distance, then prefer closer to center-ish to reduce corner traps,
            # then deterministic by target coords.
            adv = (opd - myd)
            center = - (abs(tx - (w - 1) / 2.0) + abs(ty - (h - 1) / 2.0))
            # If opponent is much closer, deprioritize unless we still have a shot (myd <= opd).
            shot_bonus = 200 if myd <= opd else 0
            key = (adv, shot_bonus, -myd, center, -opp_prox, -obs_pen, -tx, -ty)

            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue

        # Add repulsion: maximize distance from opponent (when not already strongly winning)
        # to avoid mirroring their nearest-resource path.
        repulse = man(nx, ny, ox, oy)
        final_key = (local_best[0], local_best[1], local_best[2], local_best[3], repulse, local_best)
        if best_key is None or final_key > best_key:
            best_key = final_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]