def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_val = None
    best_move = [0, 0]

    # One-step lookahead: pick our immediate move that maximizes our best "grab" advantage.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Score after taking this move: choose the resource we would be best positioned to collect first.
        best_adv = None
        best_tie = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_us = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # If we can't reasonably arrive sooner, devalue strongly.
            adv = d_op - d_us
            if adv < 0:
                adv *= 1.2  # still consider, but less attractive
            # Prefer resources aligned with opponent's column/row to enable denial.
            deny = 0.0
            if rx == ox: deny += 0.6
            if ry == oy: deny += 0.6
            # Prefer closer target to avoid committing too far.
            closeness = -0.08 * d_us
            # Small tie-break for determinism: prefer smaller (rx,ry).
            tie = (-abs(rx - ox) - abs(ry - oy), rx, ry)
            val = adv + deny + closeness
            if best_adv is None or val > best_adv or (val == best_adv and tie < best_tie):
                best_adv = val
                best_tie = tie

        if best_adv is None:
            continue

        # Additional safety: if current move doesn't improve our immediate advantage, nudge toward staying safe.
        # Prefer moves that do not increase our distance to the chosen "best target by current eval".
        # Deterministic tie-break by move order.
        if best_val is None or best_adv > best_val:
            best_val = best_adv
            best_move = [dx, dy]
        elif best_adv == best_val:
            # Deterministic tie-break: prefer not moving diagonally; then prefer lexicographically smaller move.
            cur_diag = (best_move[0] != 0 and best_move[1] != 0)
            cand_diag = (dx != 0 and dy != 0)
            if cur_diag and not cand_diag:
                best_move = [dx, dy]
            elif cand_diag == cur_diag and (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]