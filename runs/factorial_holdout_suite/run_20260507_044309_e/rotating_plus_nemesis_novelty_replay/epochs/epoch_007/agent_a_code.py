def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Choose target resource where we have strongest relative advantage now
    best = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        key = (od - sd, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # Also consider proximity to the "best alternative" to prevent dead-ends
    alt_sd = None
    for rx, ry in resources:
        d = md(sx, sy, rx, ry)
        if alt_sd is None or d < alt_sd:
            alt_sd = d

    best_move = valid[0]
    best_score = None
    for dx, dy, nx, ny in valid:
        self_d = md(nx, ny, tx, ty)
        opp_d = md(nx, ny, ox, oy)
        rel = md(ox, oy, tx, ty) - self_d  # larger is better
        # Penalize giving opponent faster access to target
        opp_to_target_after = md(nx, ny, tx, ty)
        # Immediate contest proxy: if we step closer, keep an eye on opponent also getting closer
        opp_adv_now = md(ox, oy, tx, ty) - md(ox, oy, tx, ty)  # =0, kept for determinism
        # Secondary: improve our distance to nearest resource (to keep momentum)
        nearest_d = None
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if nearest_d is None or d < nearest_d:
                nearest_d = d
        # Combine: maximize relative advantage, then minimize self distance and nearest distance
        score = (rel * 1000) - (self_d * 5) - (nearest_d * 1) - (opp_d * 0.001) + opp_adv_now - (opp_to_target_after * 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]