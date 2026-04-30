def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cd(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    # Pick a target resource where we're relatively closer than the opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cd(sx, sy, rx, ry)
        do = cd(ox, oy, rx, ry)
        # Prefer resources where we can beat opponent; slight preference to nearer ones.
        key = (do - ds, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    # If no resources, just move to improve position toward center.
    if best is None:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        def score_pos(px, py):
            return -(abs(px - tx) + abs(py - ty))
        best_move = (0, 0)
        best_s = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                s = score_pos(nx, ny)
                if best_s is None or s > best_s:
                    best_s = s
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    rx, ry = best

    # Obstacle-avoiding move: minimize distance to target, maximize distance from opponent.
    target_dist = None
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_target = cd(nx, ny, rx, ry)
        d_opp = cd(nx, ny, ox, oy)
        # Move only; don't overly chase if opponent is about to reach target.
        # Tie-break deterministically by coordinates.
        key = (-(d_target), d_opp, nx, ny, dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    if best_move == (0, 0):
        # Fallback: allow staying if all moves blocked.
        return [0, 0]
    return [best_move[0], best_move[1]]