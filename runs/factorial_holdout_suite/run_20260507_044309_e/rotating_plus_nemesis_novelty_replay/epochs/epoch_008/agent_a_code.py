def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # If opponent is closer to some resource, prioritize denying it; otherwise go for best relative advantage.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        deny = (sd - od)  # smaller => we are closer; larger => opponent closer
        key = (deny, -(sd - od), -sd, rx, ry)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        self_to_t = md(nx, ny, tx, ty)
        opp_to_t = md(nx, ny, ox, oy)

        # Strongly prioritize reducing distance to target.
        # Secondary: keep opponent farther from our target (avoid enabling capture race).
        # Tertiary: avoid stepping into positions where opponent is closer to target than us.
        opp_to_target = md(nx, ny, tx, ty)
        our_after = md(nx, ny, tx, ty)
        opp_adv = md(ox, oy, tx, ty) - opp_to_target  # higher => opponent farther from target relative to us

        # Also slightly prefer moves that bring us closer to any currently visible resource.
        nearest_any = None
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if nearest_any is None or d < nearest_any:
                nearest_any = d

        score = (self_to_t, -opp_adv, nearest_any, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]