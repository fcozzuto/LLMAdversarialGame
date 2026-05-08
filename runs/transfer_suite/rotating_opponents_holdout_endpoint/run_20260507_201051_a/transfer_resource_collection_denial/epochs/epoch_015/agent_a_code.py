def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target resources where we can beat opponent in reach-time; break ties deterministically.
    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer cells we reach no later, and more margin; then closer for us.
        score = (do - ds, -(ds), rx, ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry), ds, do)

    if best is None:
        return [0, 0]

    (tx, ty) = best[1]

    # Deterministically pick move that most reduces distance to target and avoids obstacles.
    # Candidate order favors diagonal, then horizontal/vertical, then stay.
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        # Secondary objective: also avoid letting opponent get strictly closer to the same target.
        no = man(ox, oy, tx, ty)
        margin = no - nd
        key = (-(nd), -margin, dx, dy)
        if best_m is None or key > best_m[0]:
            best_m = (key, (dx, dy))

    if best_m is None:
        # If all moves blocked, try staying if valid else return [0,0] (engine keeps us in place).
        return [0, 0]

    return [best_m[1][0], best_m[1][1]]