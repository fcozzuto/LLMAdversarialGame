def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for grid with diagonals

    best_target = None
    best_key = (-10**18, -10**18, None)
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        gap = od - sd  # positive means we are closer (or equal)
        # tie-break: prefer closer overall if same gap
        key = (gap, -sd, (rx, ry))
        if key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # Evaluate each move toward target and also try to keep (or increase) lead on target
    best_mv = None
    best_score = -10**18
    for dx, dy, nx, ny in valid:
        sd2 = md(nx, ny, tx, ty)
        od2 = md(ox, oy, tx, ty)
        gap2 = od2 - sd2
        # small penalty for moving away from target compared to current
        cur_d = md(sx, sy, tx, ty)
        away_pen = 0 if sd2 <= cur_d else (sd2 - cur_d)
        # mild preference to move if it reduces distance to any resource behind
        score = gap2 * 100 - sd2 - away_pen
        if score > best_score:
            best_score = score
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]