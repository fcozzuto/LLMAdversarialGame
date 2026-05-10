def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Deterministic fallback: head to corner opposite our start (bias breaks symmetry with opponent)
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        best = None
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - 0.001 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]

    best = [0, 0]
    bestv = -10**18
    # Evaluate each candidate move by the best "racing advantage" resource.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # If we could collect immediately, strongly prefer it.
        value = 0.0
        best_adv = -10**18
        best_self_d = 10**9
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)

            # Collecting immediately gets a large bonus.
            if self_d == 0:
                adv = 10**6
            else:
                adv = (opp_d - self_d)  # positive means we're closer (race win)
                # If opponent is also close, slight prefer larger lead and not too far.
                adv = adv - 0.05 * (self_d - opp_d if opp_d < self_d else self_d)

            # Choose the single most promising resource for this move.
            if adv > best_adv or (adv == best_adv and self_d < best_self_d):
                best_adv = adv
                best_self_d = self_d

        # Encourage moves that reduce our distance to the currently best target;
        # also add a small term to avoid standing still unless it's best.
        move_pen = 0.0 if (dx == 0 and dy == 0) else -0.02
        value = best_adv - 0.002 * best_self_d + move_pen

        # Minor deterministic nudge: avoid moves that get closer to obstacles indirectly handled by legal()
        if value > bestv:
            bestv = value
            best = [dx, dy]

    return best