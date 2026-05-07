def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if (sx, sy) in resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)

        # If we can arrive no later than opponent, prioritize strongly.
        # Otherwise, still allow a contested grab only if opponent advantage is small.
        if sd <= od:
            adv = od - sd  # bigger => we are better positioned
            key = (-adv, sd, rx + 13 * ry)
        else:
            gap = sd - od  # smaller => closer race
            # Discourage large losing races; prefer resources slightly closer to us.
            key = (gap, od, sd, rx + 13 * ry)

        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Primary: reduce distance to chosen target
        nd = md(nx, ny, tx, ty)
        # Secondary: don't step into opponent's immediate neighborhood if it worsens
        opp_close = (md(nx, ny, ox, oy) <= 1)
        # Tertiary tie-break: deterministic ordering via coordinates
        key = (nd, 1 if opp_close else 0, (nx + 7 * ny), abs(dx) + abs(dy))
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]