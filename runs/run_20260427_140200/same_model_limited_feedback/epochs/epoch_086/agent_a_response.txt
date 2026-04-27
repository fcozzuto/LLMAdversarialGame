def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # Prefer contesting resources near the center and near our reach while keeping distance from opponent.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Precompute best resource target deterministically
    if resources:
        best_target = None
        best_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = dist2(sx, sy, rx, ry)
            d_opp = dist2(ox, oy, rx, ry)
            center_bias = -0.0008 * (rx - cx) ** 2 - 0.0008 * (ry - cy) ** 2
            # Contest: prefer resources closer than opponent, and near center.
            val = -0.9 * d_self + 0.6 * d_opp + center_bias
            # Break ties deterministically by coordinates
            if val > best_val or (val == best_val and (rx, ry) < best_target):
                best_val = val
                best_target = (rx, ry)
        tx, ty = best_target
    else:
        # No resources visible: head toward center to avoid useless looping
        tx, ty = int(round(cx)), int(round(cy))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        # If we are already on a resource, stay (or move only if it improves opponent blocking)
        here_resource = (nx, ny) in set(tuple(p) for p in resources)
        d_self = dist2(nx, ny, tx, ty)
        d_opp = dist2(nx, ny, ox, oy)
        # Bonus for reducing distance to our target; bonus for pushing our position away from opponent
        # and slight penalty for being too close to opponent to avoid being mirrored.
        score = -d_self + 0.55 * d_opp
        # Secondary objective: move to reduce opponent's progress toward the same target
        opp_to_target = dist2(ox, oy, tx, ty)
        opp_after = dist2(ox, oy, tx, ty)  # we can't control opponent directly; keep deterministic structure
        score += -0.0001 * opp_after
        # Deterministic tie-breaker: prefer larger dx,dy patterns toward right/down, then stay
        tie = (dx + 1) * 10 + (dy + 1)
        if score > best[0] or (score == best[0] and tie < best[1]):
            best = (score, tie, 0)

    # If best is unset (all moves blocked), stay
    chosen_dx, chosen_dy = moves[0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        d_self = dist2(nx, ny, tx, ty)
        d_opp = dist2(nx, ny, ox, oy)
        score = -d_self + 0.55 * d_opp
        tie = (dx + 1) * 10 + (dy + 1)
        if score == best[0] and tie == best[1]:
            chosen_dx, chosen_dy = dx, dy
            break
    return [int(chosen_dx), int(chosen_dy)]